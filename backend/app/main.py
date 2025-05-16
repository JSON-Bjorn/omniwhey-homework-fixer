import logging
import time
import os
import sys
from contextlib import asynccontextmanager
from typing import Callable
from pathlib import Path

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from app.api.api import api_router
from app.core.config import settings
from app.utils import setup_logging
from app.db.init_db import init_db
from app.db.session import engine, create_tables, init_limiter
from app.utils.db_maintenance import run_maintenance_tasks
from app.utils.rate_limit import RateLimitMiddleware

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Paths
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES_PATH = BASE_PATH / "templates"

# Set up templates
templates = Jinja2Templates(directory=str(TEMPLATES_PATH))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize services on app startup and clean up on shutdown
    """
    # Startup
    logger.info("Starting application")
    try:
        await create_tables()
        logger.info("Database tables created")

        # Start maintenance tasks in background
        if settings.ENABLE_DB_MAINTENANCE:
            logger.info("Initializing database maintenance tasks")
            await run_maintenance_tasks()
    except Exception as e:
        logger.error(
            f"Error during application startup: {str(e)}", exc_info=True
        )

    yield

    # Shutdown
    logger.info("Shutting down application")
    if engine:
        logger.info("Closing database connection pool")
        await engine.dispose()
        logger.info("Database connection pool closed")


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

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)
logger.info(
    "Rate limiting middleware added with limit of {} requests per minute".format(
        settings.RATE_LIMIT_DEFAULT
    )
)


# Add middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    """Log request information and timing."""
    start_time = time.time()
    path = request.url.path
    method = request.method

    # Skip health check endpoint for request logging to avoid noise
    if not path.startswith("/api/health"):
        logger.info(f"Request {method} {path}")

    try:
        response = await call_next(request)

        # Log response time
        process_time = time.time() - start_time
        if not path.startswith("/api/health"):
            logger.info(
                f"Response {method} {path} - Status: {response.status_code}, "
                f"Time: {process_time:.3f}s"
            )

        return response
    except Exception as exc:
        # Log unhandled exceptions
        logger.error(
            f"Unhandled exception in {method} {path}: {str(exc)}",
            exc_info=True,
        )

        # Return a JSON error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


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


# Mount template directory for emails
if os.path.exists(str(TEMPLATES_PATH)):
    app.mount(
        "/templates",
        StaticFiles(directory=str(TEMPLATES_PATH)),
        name="templates",
    )
else:
    logger.warning(f"Templates directory not found at {TEMPLATES_PATH}")
