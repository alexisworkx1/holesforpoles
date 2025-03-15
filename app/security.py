import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.schemas import TokenPayload


# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, int], 
    expires_delta: Optional[timedelta] = None,
    scopes: list = []
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Subject of the token (typically user ID)
        expires_delta: Optional expiration time
        scopes: Optional list of permission scopes
        
    Returns:
        JWT token as string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "scopes": scopes
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate JWT access token.
    
    Args:
        token: JWT token
        
    Returns:
        TokenPayload if valid, None if invalid
        
    Raises:
        ValueError: If token validation fails
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise ValueError("Token expired")
            
        return token_data
    except (jwt.JWTError, ValidationError) as e:
        raise ValueError(f"Invalid token: {str(e)}")


def get_user_id_from_token(token: str) -> Optional[Union[str, int]]:
    """Extract user ID from token."""
    try:
        token_data = decode_access_token(token)
        return token_data.sub
    except ValueError:
        return None

