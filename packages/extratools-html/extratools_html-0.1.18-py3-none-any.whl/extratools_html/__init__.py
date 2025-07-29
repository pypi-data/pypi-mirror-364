from __future__ import annotations

import asyncio
import ssl
from collections.abc import Iterable
from contextlib import suppress
from datetime import timedelta
from enum import StrEnum
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import urlparse

import backoff
import httpx
import minify_html
import truststore
from blob_dict.blob import StrBlob
from blob_dict.dict.path import LocalPath, PathBlobDict
from extratools_core.path import cleanup_dir_by_ttl
from extratools_core.typing import PathLike
from html2text import HTML2Text

with suppress(ImportError):
    from playwright.async_api import Browser, async_playwright, expect
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .cleanup import cleanup_page

MAX_TRIES: int = 3
MAX_TIMEOUT: int = 60
REQUEST_TIMEOUT: int = 10
# In milliseconds
PRE_ACTION_TIMEOUT: int = 10 * 1_000

ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

# TODO: Make cache path/TTL configurable via configuration file (in TOML).
# It will also allow support for other non-local path (like `CloudPath`).
CACHE_PATH: PathLike = LocalPath("~/.http-cache").expanduser()
CACHE_TTL: timedelta = timedelta(days=1)

cache = PathBlobDict(CACHE_PATH, blob_class=StrBlob, ttl=CACHE_TTL)
cache.create()

# Trigger cleanup here as we do not have CRON job or daemon process
# If available, native solution is preferred (like S3's object lifecycle management).
# Use longer TTL here than cache TTL in case we still somehow need raw data
list(cleanup_dir_by_ttl(CACHE_PATH, timedelta(days=30)))


KEEP_CLICK_INTERVAL: timedelta = timedelta(seconds=5)
KEEP_CLICK_MAX_TRIES: int = 100

KEEP_SCROLL_TO_BE_VISIBLE_INTERVAL: timedelta = timedelta(seconds=5)
KEEP_SCROLL_TO_BE_VISIBLE_MAX_TRIES: int = 100


class PageElementAction(StrEnum):
    CLICK = "click"
    KEEP_CLICK = "keep_click"
    TO_BE_VISIBLE = "to_be_visible"
    KEEP_SCROLL_TO_BE_VISIBLE = "keep_scroll_to_be_visible"


async def __download_via_request(
    page_url: str,
    *,
    user_agent: str | None = None,
) -> str | None:
    # https://www.python-httpx.org/advanced/ssl/
    async with httpx.AsyncClient(verify=ctx) as client:
        response: httpx.Response = await client.get(
            page_url,
            follow_redirects=True,
            timeout=REQUEST_TIMEOUT,
            headers=(
                {
                    "User-Agent": user_agent,
                } if user_agent
                else {}
            ),
        )

    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        # It also triggers backoff if necessary
        return None

    response.raise_for_status()

    return response.text


async def __download_via_browser(
    page_url: str,
    *,
    user_agent: str | None = None,
    pre_actions: Iterable[tuple[str, PageElementAction]] | None = None,
) -> str | None:
    async with async_playwright() as playwright:  # pyright: ignore [reportPossiblyUnboundVariable]
        browser: Browser = await playwright.chromium.launch()
        await browser.new_context(
            user_agent=user_agent,
        )

        page = await browser.new_page()
        await page.route(
            "**/*",
            lambda route: (
                route.abort()
                # https://playwright.dev/python/docs/api/class-request#request-resource-type
                if route.request.resource_type in {
                    "font",
                    "image",
                    "media",
                }
                else route.continue_()
            ),
        )
        response = await page.goto(page_url)
        if not response:
            return None
        if response.status == HTTPStatus.TOO_MANY_REQUESTS:
            # It also triggers backoff if necessary
            return None

        for selector, action in pre_actions or []:
            with suppress(AssertionError, PlaywrightTimeoutError):  # pyright: ignore [reportPossiblyUnboundVariable]
                match action:
                    case PageElementAction.CLICK:
                        await page.locator(selector).click(
                            timeout=PRE_ACTION_TIMEOUT,
                            # Allow click even current element is covered by other elements.
                            # Otherwise, other pre-actions are needed before this pre-action
                            # to dismiss those covering elements.
                            # However, it is possible that dismissing those covering elements
                            # is necessary logic for page to function properly.
                            force=True,
                        )
                    case PageElementAction.KEEP_CLICK:
                        for _ in range(KEEP_CLICK_MAX_TRIES):
                            if not await page.locator(selector).is_visible():
                                break

                            await asyncio.sleep(KEEP_CLICK_INTERVAL.total_seconds())

                            await page.locator(selector).click(
                                timeout=PRE_ACTION_TIMEOUT,
                                force=True,
                            )

                    case PageElementAction.TO_BE_VISIBLE:
                        await expect(page.locator(selector)).to_be_visible(  # pyright: ignore [reportPossiblyUnboundVariable]
                            timeout=PRE_ACTION_TIMEOUT,
                        )
                    case PageElementAction.KEEP_SCROLL_TO_BE_VISIBLE:
                        for _ in range(KEEP_SCROLL_TO_BE_VISIBLE_MAX_TRIES):
                            await asyncio.sleep(KEEP_SCROLL_TO_BE_VISIBLE_INTERVAL.total_seconds())

                            while not await page.locator(selector).is_visible():
                                await page.mouse.wheel(0, 1000)

        html: str = await page.content()

        await browser.close()

    return html


def get_cache_key(page_url: str) -> str:
    parse_result = urlparse(page_url)

    # Need to handle reserved characters for filename
    # https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words
    root_dir: str = parse_result.netloc.replace(":", "_")

    path: str = parse_result.path or "/"
    # Add default filename
    if path.endswith("/"):
        path += "?"

    if parse_result.query:
        if not path.endswith("/?"):
            path += "?"
        path += parse_result.query

    return root_dir + path


@backoff.on_predicate(
    backoff.expo,
    max_tries=MAX_TRIES,
    max_time=MAX_TIMEOUT,
)
async def download_page_async(
    page_url: str,
    *,
    cleanup: bool = False,
    text_only: bool = False,
    minify: bool = True,
    user_agent: str | None = None,
    use_browser: bool = False,
    pre_actions: Iterable[tuple[str, PageElementAction]] | None = None,
    use_cache: bool = True,
) -> str | None:
    page_html: str | None
    cache_key: str = get_cache_key(page_url)

    if use_cache and (cache_blob := cache.get(cache_key)):
        page_html = cast("StrBlob", cache_blob).as_str()
    elif use_browser:
        page_html = await __download_via_browser(
            page_url,
            user_agent=user_agent,
            pre_actions=pre_actions,
        )
    else:
        page_html = await __download_via_request(
            page_url,
            user_agent=user_agent,
        )
    if page_html is None:
        return None

    cache[cache_key] = StrBlob(page_html)

    if minify:
        page_html = minify_html.minify(page_html)

    if cleanup:
        page_html = await cleanup_page(page_html)

    if text_only:
        h = HTML2Text()
        h.ignore_images = True
        h.ignore_links = True
        return h.handle(page_html)

    return page_html


def download_page(
    page_url: str,
    **kwargs: Any,
) -> str | None:
    return asyncio.run(download_page_async(
        page_url,
        **kwargs,
    ))
