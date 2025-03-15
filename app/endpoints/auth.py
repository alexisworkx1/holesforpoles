from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.database import get_db

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Dependencies
async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get current user from token.
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        User model if authenticated
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        token_data = security.decode_access_token(token)
        user_id = token_data.sub
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# Routes
@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: schemas.UserCreate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If user with email or username already exists
    """
    # Check if user with email already exists
    user_by_email = db.query(models.User).filter(models.User.email == user_data.email).first()
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if user with username already exists
    user_by_username = db.query(models.User).filter(models.User.username == user_data.username).first()
    if user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create new user
    hashed_password = security.get_password_hash(user_data.password)
    user = models.User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Log in and get access token.
    
    Args:
        form_data: Username and password
        db: Database session
        
    Returns:
        Access token
        
    Raises:
        HTTPException: If authentication fails
    """
    # Try to find user by username
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    # If not found, try with email
    if not user:
        user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # If still not found or password doesn't match, raise error
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If user is not active, raise error
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = security.create_access_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=schemas.User)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return current_user


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    current_user: models.User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Refresh access token.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        New access token
    """
    access_token = security.create_access_token(subject=current_user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

