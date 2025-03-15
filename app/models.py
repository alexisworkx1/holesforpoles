from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from app.database import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """SQLAlchemy User model for authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def verify_password(self, plain_password: str) -> bool:
        """Verify password against stored hash."""
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash from plain text password."""
        return pwd_context.hash(password)

