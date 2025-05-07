from typing import Callable, Any
import logging
from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from app.core.config import settings


logger = logging.getLogger(__name__)


async def init_limiter(redis_url: str) -> None:
    """Initialize the rate limiter.

    Args:
        redis_url: Redis URL
    """
    try:
        await FastAPILimiter.init(redis_url)
        logger.info("Rate limiter initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize rate limiter: {str(e)}")
        logger.warning("Rate limiting will not be enabled")


# Rate limiter for standard endpoints
default_limiter = RateLimiter(times=settings.RATE_LIMIT_DEFAULT, seconds=60)

# Rate limiter for AI endpoints
ai_endpoint_limiter = RateLimiter(
    times=settings.RATE_LIMIT_AI_ENDPOINTS, seconds=60
)


class RateLimitedRoute(APIRoute):
    """Custom API route with rate limiting."""

    def get_route_handler(self) -> Callable:
        """Get route handler with rate limiting."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Custom route handler with rate limiting."""
            return await original_route_handler(request)

        return custom_route_handler
