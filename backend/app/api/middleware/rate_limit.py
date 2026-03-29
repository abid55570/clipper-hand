import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as aioredis
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-backed sliding window rate limiter."""

    def __init__(self, app, redis_url: str = None):
        super().__init__(app)
        self.redis_url = redis_url or settings.redis_url
        self.max_requests = settings.rate_limit_requests
        self.window_seconds = settings.rate_limit_window_seconds
        self._redis = None

    async def _get_redis(self):
        if self._redis is None:
            try:
                self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
            except Exception:
                logger.warning("rate_limit_redis_unavailable")
                return None
        return self._redis

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ("/health", "/api/v1/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        redis_client = await self._get_redis()

        if redis_client:
            try:
                key = f"rate_limit:{client_ip}"
                now = time.time()
                window_start = now - self.window_seconds

                pipe = redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {str(now): now})
                pipe.expire(key, self.window_seconds)
                results = await pipe.execute()

                request_count = results[1]

                if request_count >= self.max_requests:
                    logger.warning("rate_limit_exceeded", client_ip=client_ip, count=request_count)
                    return JSONResponse(
                        status_code=429,
                        content={"error": "Rate limit exceeded. Try again later."},
                        headers={"Retry-After": str(self.window_seconds)},
                    )
            except Exception:
                logger.warning("rate_limit_check_failed", client_ip=client_ip)

        return await call_next(request)
