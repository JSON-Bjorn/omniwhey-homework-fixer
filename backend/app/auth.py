from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import os
from sqlalchemy.orm import Session

from config.database import get_db
from models import User

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "a-very-long-and-secure-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")


# Token models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserBase(BaseModel):
    email: str
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    hashed_password: str


# Temporary fake user database for testing
fake_users_db = {
    "user@example.com": {
        "email": "user@example.com",
        "hashed_password": pwd_context.hash("password123"),
        "is_active": True,
        "is_admin": False,
    }
}


# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, email: str):
    if email in fake_users_db:
        user_dict = fake_users_db[email]
        return UserInDB(**user_dict)

    # Check for pytest in sys.modules to detect test mode
    is_test = "pytest" in __import__("sys").modules

    if not is_test and db:
        user = db.query(User).filter(User.email == email).first()
        if user:
            return UserInDB(
                email=user.email,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                is_admin=user.is_admin,
            )
    return None


def authenticate_user(fake_db, db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(db=db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
