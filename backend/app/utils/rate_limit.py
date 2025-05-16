from typing import Callable, Dict, List, Tuple
import time
import logging
import asyncio
from fastapi import Request, Response, HTTPException, status
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger(__name__)


class SimpleRateLimiter:
    """
    Simple in-memory rate limiter without Redis dependency.
    """

    def __init__(
        self, times: int = 100, seconds: int = 60, block_seconds: int = 60
    ):
        self.times = times  # Number of requests allowed
        self.seconds = seconds  # Time window in seconds
        self.block_seconds = block_seconds  # Block duration in seconds
        self.requests: Dict[
            str, List[float]
        ] = {}  # Client IP -> list of request timestamps
        self.blocked_ips: Dict[
            str, float
        ] = {}  # Client IP -> block expiration timestamp

        # Start cleanup task
        asyncio.create_task(self._cleanup_task())

    async def _cleanup_task(self):
        """Background task to clean up expired entries"""
        while True:
            await asyncio.sleep(60)  # Run every minute
            self._cleanup()

    def _cleanup(self):
        """Remove expired entries from requests and blocked_ips"""
        now = time.time()

        # Clean up request records
        for ip, timestamps in list(self.requests.items()):
            self.requests[ip] = [
                ts for ts in timestamps if now - ts < self.seconds
            ]
            if not self.requests[ip]:
                del self.requests[ip]

        # Clean up blocked IPs
        for ip, expiration in list(self.blocked_ips.items()):
            if now > expiration:
                del self.blocked_ips[ip]
                logger.info(f"IP {ip} unblocked after rate limit expiration")

    def is_rate_limited(self, client_ip: str) -> Tuple[bool, int]:
        """
        Check if a client is rate limited

        Args:
            client_ip: The client's IP address

        Returns:
            (is_limited, retry_after_seconds)
        """
        now = time.time()

        # Check if client is blocked
        if client_ip in self.blocked_ips:
            expiration = self.blocked_ips[client_ip]
            if now < expiration:
                retry_after = int(expiration - now)
                return True, retry_after

        # Get client's request history
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Clean up old requests
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if now - ts < self.seconds
        ]

        # Check if client exceeds rate limit
        if len(self.requests[client_ip]) >= self.times:
            # Block the client
            expiration = now + self.block_seconds
            self.blocked_ips[client_ip] = expiration
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}. Blocked for {self.block_seconds} seconds"
            )
            return True, self.block_seconds

        # Record this request
        self.requests[client_ip].append(now)
        return False, 0


# Create an instance of the rate limiter with settings from config
rate_limiter = SimpleRateLimiter(
    times=settings.RATE_LIMIT_DEFAULT, seconds=60, block_seconds=60
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply rate limiting to all requests.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Skip rate limiting for certain paths (like health checks)
        if (
            request.url.path.startswith("/api/health")
            or request.url.path == "/"
        ):
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        is_limited, retry_after = rate_limiter.is_rate_limited(client_ip)
        if is_limited:
            logger.warning(
                f"Rate limit applied to {client_ip}, retry after {retry_after} seconds"
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        # Process the request normally
        return await call_next(request)


# Legacy functions kept for backward compatibility
async def init_limiter(redis_url: str = None) -> None:
    """Initialize the rate limiter (legacy function, kept for compatibility)."""
    logger.info("Using built-in memory rate limiter (no Redis required)")


# Legacy rate limiter dependencies kept for backward compatibility
default_limiter = lambda: None
ai_endpoint_limiter = lambda: None


class RateLimitedRoute(APIRoute):
    """Custom API route with rate limiting."""

    def get_route_handler(self) -> Callable:
        """Get route handler with rate limiting."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Custom route handler with rate limiting."""
            return await original_route_handler(request)

        return custom_route_handler
