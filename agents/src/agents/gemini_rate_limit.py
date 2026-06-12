"""Client-side Gemini rate limiting and 429 retry helpers for Google ADK runners."""

from __future__ import annotations

import asyncio
import logging
import os
import random
import re
import time
from collections import deque
from collections.abc import AsyncIterator
from typing import Any

from google.genai.errors import ClientError

logger = logging.getLogger(__name__)

_RETRY_AFTER_SECONDS = re.compile(r"retry in ([\d.]+)s", re.IGNORECASE)


class SlidingWindowRateLimiter:
    """Limits requests to `max_requests` per `window_seconds` (default: 15 RPM)."""

    def __init__(self, max_requests: int, window_seconds: float = 60.0) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._timestamps: deque[float] = deque()

    async def acquire(self) -> None:
        while True:
            now = time.monotonic()
            while self._timestamps and now - self._timestamps[0] >= self._window_seconds:
                self._timestamps.popleft()

            if len(self._timestamps) < self._max_requests:
                self._timestamps.append(now)
                return

            wait = self._window_seconds - (now - self._timestamps[0])
            await asyncio.sleep(max(wait, 0.05))


def is_gemini_rate_limit_error(exc: BaseException) -> bool:
    if isinstance(exc, ClientError) and exc.code == 429:
        return True
    message = str(exc).lower()
    return (
        "429" in message
        or "resource_exhausted" in message
        or "quota exceeded" in message
        or "rate limit" in message
    )


def is_permanent_quota_exhaustion(exc: BaseException) -> bool:
    """Daily free-tier quota exhausted — retries won't help until the quota resets."""
    message = str(exc).lower()
    if _RETRY_AFTER_SECONDS.search(str(exc)):
        return False
    if "perday" in message or "per_day" in message:
        return True
    return "limit: 0" in message and "free_tier" in message


def retry_delay_seconds(exc: BaseException, attempt: int, *, base: float = 1.0, cap: float = 60.0) -> float:
    match = _RETRY_AFTER_SECONDS.search(str(exc))
    if match:
        delay = min(cap, float(match.group(1)))
    else:
        delay = min(cap, base * (2**attempt))
    return delay + random.uniform(0, delay * 0.25)


def rate_limiter_from_env() -> SlidingWindowRateLimiter:
    rpm = int(os.environ.get("GEMINI_RPM_LIMIT", "15"))
    window = float(os.environ.get("GEMINI_RATE_WINDOW_SECONDS", "60"))
    return SlidingWindowRateLimiter(max_requests=rpm, window_seconds=window)


def max_retries_from_env() -> int:
    return int(os.environ.get("GEMINI_MAX_RETRIES", "5"))


async def run_async_with_rate_limit_and_retry(
    runner: Any,
    *,
    rate_limiter: SlidingWindowRateLimiter | None = None,
    max_retries: int | None = None,
    **run_kwargs: Any,
) -> AsyncIterator[Any]:
    """Wrap `runner.run_async` with RPM throttling and exponential backoff on 429."""
    limiter = rate_limiter or rate_limiter_from_env()
    retries = max_retries if max_retries is not None else max_retries_from_env()

    for attempt in range(retries + 1):
        await limiter.acquire()
        try:
            async for event in runner.run_async(**run_kwargs):
                yield event
            return
        except Exception as exc:
            if not is_gemini_rate_limit_error(exc):
                raise
            if is_permanent_quota_exhaustion(exc):
                raise RuntimeError(
                    "Gemini free-tier daily quota is exhausted. "
                    "Upgrade to pay-as-you-go in Google AI Studio "
                    "(https://aistudio.google.com/) or reduce request volume."
                ) from exc
            if attempt >= retries:
                raise RuntimeError(
                    f"Gemini API rate limit exceeded after {retries + 1} attempts. "
                    "Upgrade to pay-as-you-go in Google AI Studio "
                    "(https://aistudio.google.com/) or lower concurrency via GEMINI_RPM_LIMIT."
                ) from exc
            delay = retry_delay_seconds(exc, attempt)
            logger.warning(
                "Gemini rate limited (attempt %s/%s), retrying in %.1fs: %s",
                attempt + 1,
                retries + 1,
                delay,
                exc,
            )
            await asyncio.sleep(delay)
