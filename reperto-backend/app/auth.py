# backend/app/auth.py
import os
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from .database import USERS_DB  # Import in-memory store

pwd_ctx = CryptContext(schemes=["argon2"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

async def create_user(name: str, email: str, password: str):
    # Check if user already exists
    if email in USERS_DB:
        return False

    # Truncate password to 72 bytes for bcrypt/argon2 compatibility
    password = password[:72]
    hashed = pwd_ctx.hash(password)
    
    # Store in memory
    USERS_DB[email] = {
        "name": name,
        "email": email,
        "password_hash": hashed
    }
    return True


async def authenticate_user(email: str, password: str):
    # Truncate password to match creation
    password = password[:72]

    # Retrieve from memory
    user = USERS_DB.get(email)
    if not user:
        return None

    if not pwd_ctx.verify(password, user["password_hash"]):
        return None

    access_token = create_access_token(user["email"])
    return access_token


def create_access_token(subject: str, expires_delta: int | None = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
