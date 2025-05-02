from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel
import os
import sys
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Add parent directory to path for reliable imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import system modules
from app.middleware.rate_limiter import RateLimiter
from config.database import SessionLocal, engine, Base
from models import User
from app.auth import (
    authenticate_user,
    create_access_token,
    Token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user,
    UserInDB,
)

# Create FastAPI app
app = FastAPI(
    title="OmniWhey API",
    description="API for OmniWhey homework management system",
    version="1.0.0",
    docs_url="/api/swagger",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Check if running in test mode
is_test = "pytest" in sys.modules

# Create database tables
if not is_test:
    Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

# Import routes - moved after auth imports to avoid circular imports
from app.routes import routers


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*"])

# Add rate limiting middleware
app.middleware("http")(
    RateLimiter(
        requests_limit=int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100")),
        window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
        block_duration_seconds=int(os.getenv("RATE_LIMIT_BLOCK_DURATION", "300")),
    )
)

# Include routers
for router in routers:
    app.include_router(router)


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    print(f"Login attempt with username: {form_data.username}")
    user = authenticate_user(None, db, form_data.username, form_data.password)
    if not user:
        print(f"Authentication failed for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    print(f"Authentication successful for: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


# Login form data
class LoginForm(BaseModel):
    email: str
    password: str


@app.post("/api/login")
async def login(login_data: LoginForm, db: Session = Depends(get_db)):
    user = authenticate_user(None, db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@app.get("/")
async def root():
    return {"message": "Welcome to OmniWhey API"}


@app.get("/users/me")
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    # Check if the request is for Swagger UI
    path = request.url.path
    if (
        path.startswith("/api/swagger")
        or path.startswith("/api/openapi")
        or path.startswith("/api/redoc")
    ):
        # Relaxed CSP for documentation endpoints
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )
    else:
        # Strict CSP for other endpoints
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'"
        )

    return response
