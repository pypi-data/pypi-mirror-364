import asyncio
import logging
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    import httpx


async def fetch_with_retry(
    client: "httpx.AsyncClient",
    url: str,
    *,
    enable_logging: bool = False,
    raise_on_status_error: bool = False,
    retries: int = 5,
    initial_backoff: int = 5,
    **kwargs: Any,  # pyright: ignore[reportAny, reportExplicitAny]
) -> "httpx.Response":
    import httpx

    async def backoff(attempt: int) -> None:
        nonlocal initial_backoff
        backoff_time = initial_backoff * attempt
        if enable_logging:
            logging.warning(
                f"Request to '{url}' failed. Using backoff: {backoff_time} seconds."
            )
        await asyncio.sleep(backoff_time)

    for attempt in range(retries):
        try:
            response = await client.get(url, **kwargs)  # pyright: ignore[reportAny]
            _ = response.raise_for_status()
            return response
        except httpx.RequestError:
            if attempt == retries - 1:
                raise
            await backoff(attempt + 1)
            continue
        except httpx.HTTPStatusError as status_exception:
            if attempt == retries - 1:
                raise
            retry_after = cast(
                str, status_exception.response.headers.get("Retry-After")
            )
            if not retry_after:
                if raise_on_status_error:
                    raise
                await backoff(attempt + 1)
                continue

            retry_after_seconds = int(retry_after)
            if retry_after_seconds > 60:
                raise Exception("Too long retry time")
            if enable_logging:
                logging.warning(
                    f"Rate limited. Retrying after {retry_after_seconds} seconds."
                )
            await asyncio.sleep(retry_after_seconds)
    raise Exception(f"Failed to fetch response from: {url}")
