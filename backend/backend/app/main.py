import logging
import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import settings
from app.utils import setup_logging, create_tables, init_limiter
from app.db.init_db import init_db

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application lifespan context manager.

    Args:
        app: FastAPI application
    """
    # Startup
    logger.info("Starting up application...")

    # Create database tables
    await create_tables()

    # Initialize database with initial data
    await init_db()

    # Initialize rate limiter (if a Redis URL is provided in settings)
    # This is left as a placeholder since we haven't implemented Redis connection yet
    # redis_url = "redis://localhost:6379/0"
    # await init_limiter(redis_url)

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the Omniwhey Homework Fixer application",
    version="0.1.0",
    lifespan=lifespan,
)

# Set up CORS
if settings.ALLOWED_HOSTS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(host) for host in settings.ALLOWED_HOSTS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Add middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    """Log request information and timing."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Log request details
    logger.debug(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.4f}s with status {response.status_code}"
    )

    # Add processing time header
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Include API router
app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "documentation": "/docs",
    }
