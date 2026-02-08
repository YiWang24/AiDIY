"""Simple daily rate limiting middleware.

Limits:
- Global daily requests: 10_000
- Per-IP daily requests: 50

Notes:
- This implementation is in-memory (per process). For multi-replica deployments,
  use a shared store (e.g., Redis) to enforce limits consistently.
- Day boundary uses UTC.
"""

from __future__ import annotations

import asyncio
import ipaddress
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


@dataclass(frozen=True)
class DailyRateLimitConfig:
    global_daily_limit: int = 10_000
    per_ip_daily_limit: int = 50
    # Only apply to these path prefixes (keeps /health and /ready unaffected)
    path_prefixes: tuple[str, ...] = ("/stream",)


def _utc_day_key() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _seconds_until_utc_midnight() -> int:
    now = datetime.now(timezone.utc)
    tomorrow = (now.date()).toordinal() + 1
    midnight = datetime.fromordinal(tomorrow).replace(tzinfo=timezone.utc)
    return max(1, int((midnight - now).total_seconds()))


def get_client_ip(request: Request) -> str:
    # Prefer headers commonly set by proxies.
    for header_name in ("cf-connecting-ip", "x-real-ip", "x-forwarded-for"):
        raw = request.headers.get(header_name)
        if not raw:
            continue
        if header_name == "x-forwarded-for":
            raw = raw.split(",", 1)[0]
        ip = raw.strip()
        if not ip:
            continue
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            return ip[:64]

    if request.client and request.client.host:
        return request.client.host
    return "unknown"


class _InMemoryDailyRateLimiter:
    def __init__(self, config: DailyRateLimitConfig):
        self._config = config
        self._lock = asyncio.Lock()
        self._day_key: str | None = None
        self._global_count: int = 0
        self._ip_counts: dict[str, int] = defaultdict(int)

    async def hit(self, ip: str) -> tuple[bool, str, int, int, int]:
        """Register a hit.

        Returns:
            (allowed, reason, remaining_global, remaining_ip, reset_seconds)
        """
        async with self._lock:
            day = _utc_day_key()
            if day != self._day_key:
                self._day_key = day
                self._global_count = 0
                self._ip_counts.clear()

            reset_seconds = _seconds_until_utc_midnight()

            if self._global_count >= self._config.global_daily_limit:
                return False, "global_daily_limit", 0, 0, reset_seconds

            current_ip = self._ip_counts.get(ip, 0)
            if current_ip >= self._config.per_ip_daily_limit:
                remaining_global = max(0, self._config.global_daily_limit - self._global_count)
                return False, "per_ip_daily_limit", remaining_global, 0, reset_seconds

            self._global_count += 1
            self._ip_counts[ip] = current_ip + 1

            remaining_global = max(0, self._config.global_daily_limit - self._global_count)
            remaining_ip = max(0, self._config.per_ip_daily_limit - self._ip_counts[ip])
            return True, "ok", remaining_global, remaining_ip, reset_seconds


class DailyRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config: DailyRateLimitConfig | None = None):
        super().__init__(app)
        self._config = config or DailyRateLimitConfig()
        self._limiter = _InMemoryDailyRateLimiter(self._config)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Never rate-limit preflight and similar non-user requests.
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path or ""
        if not any(path.startswith(prefix) for prefix in self._config.path_prefixes):
            return await call_next(request)

        ip = get_client_ip(request)
        allowed, reason, remaining_global, remaining_ip, reset_seconds = await self._limiter.hit(ip)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "reason": reason,
                    "limits": {
                        "global_daily_limit": self._config.global_daily_limit,
                        "per_ip_daily_limit": self._config.per_ip_daily_limit,
                    },
                    "reset_seconds": reset_seconds,
                },
                headers={
                    "Retry-After": str(reset_seconds),
                    "X-RateLimit-Limit-Global": str(self._config.global_daily_limit),
                    "X-RateLimit-Remaining-Global": str(remaining_global),
                    "X-RateLimit-Limit-IP": str(self._config.per_ip_daily_limit),
                    "X-RateLimit-Remaining-IP": str(remaining_ip),
                    "X-RateLimit-Reset": str(reset_seconds),
                },
            )

        response = await call_next(request)
        response.headers.setdefault("X-RateLimit-Limit-Global", str(self._config.global_daily_limit))
        response.headers.setdefault("X-RateLimit-Remaining-Global", str(remaining_global))
        response.headers.setdefault("X-RateLimit-Limit-IP", str(self._config.per_ip_daily_limit))
        response.headers.setdefault("X-RateLimit-Remaining-IP", str(remaining_ip))
        response.headers.setdefault("X-RateLimit-Reset", str(reset_seconds))
        return response
