import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, List, Callable, Tuple
import asyncio


class RateLimiter:
    """
    Simple in-memory rate limiter middleware for FastAPI
    """

    def __init__(
        self,
        requests_limit: int = 100,
        window_seconds: int = 60,
        block_duration_seconds: int = 300,
    ):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.block_duration_seconds = block_duration_seconds
        self.clients: Dict[str, List[float]] = {}
        self.blocked_clients: Dict[str, float] = {}

    async def cleanup_task(self):
        """Task to clean up expired entries"""
        while True:
            await asyncio.sleep(60)  # Run every 60 seconds
            self._cleanup()

    def _cleanup(self):
        """Remove expired entries from clients and blocked_clients"""
        current_time = time.time()

        # Cleanup clients
        for client_id, timestamps in list(self.clients.items()):
            # Remove timestamps older than window_seconds
            self.clients[client_id] = [
                ts for ts in timestamps if current_time - ts < self.window_seconds
            ]
            if not self.clients[client_id]:
                del self.clients[client_id]

        # Cleanup blocked clients
        for client_id, blocked_until in list(self.blocked_clients.items()):
            if current_time > blocked_until:
                del self.blocked_clients[client_id]

    def _is_rate_limited(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if a client is rate limited

        Returns:
            Tuple[bool, int]: (is_limited, retry_after)
        """
        current_time = time.time()

        # Check if client is blocked
        if client_id in self.blocked_clients:
            blocked_until = self.blocked_clients[client_id]
            if current_time < blocked_until:
                return True, int(blocked_until - current_time)

        # Get client's request timestamps
        if client_id not in self.clients:
            self.clients[client_id] = []

        # Filter out timestamps older than window_seconds
        self.clients[client_id] = [
            ts
            for ts in self.clients[client_id]
            if current_time - ts < self.window_seconds
        ]

        # Check if client exceeds rate limit
        if len(self.clients[client_id]) >= self.requests_limit:
            # Block client
            blocked_until = current_time + self.block_duration_seconds
            self.blocked_clients[client_id] = blocked_until
            return True, self.block_duration_seconds

        # Add current timestamp to client's list
        self.clients[client_id].append(current_time)
        return False, 0

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        FastAPI middleware implementation
        """
        # Get client identifier (IP address)
        client_id = request.client.host if request.client else "unknown"

        # Check rate limit
        is_limited, retry_after = self._is_rate_limited(client_id)
        if is_limited:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        # Process the request
        return await call_next(request)
