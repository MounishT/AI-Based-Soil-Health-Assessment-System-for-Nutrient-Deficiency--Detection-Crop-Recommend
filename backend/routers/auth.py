"""
auth.py
-------
Authentication router for user registration, login, and profile.

Endpoints:
    POST /auth/register  → create a new user account
    POST /auth/login     → authenticate and receive a JWT token
    GET  /auth/me        → get current authenticated user profile
"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.deps import get_current_user
from backend.models import User
from backend.schemas import UserRegister, UserLogin, UserOut, TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ─── Password Hashing ────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Helper: Create JWT Token ────────────────────────────────────────────────
def create_access_token(user_id: int) -> str:
    """Generate a JWT access token for the given user ID."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# ─── 1. Register ─────────────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(body: UserRegister, db: Session = Depends(get_db)):
    """
    Create a new user account with email and password.

    - Returns 409 if email is already registered.
    - Returns JWT token on success (auto-login after registration).
    """
    existing = db.query(User).filter(User.email == body.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        email=body.email.lower().strip(),
        hashed_password=pwd_context.hash(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    logger.info("New user registered: %s (id=%d)", user.email, user.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


# ─── 2. Login ────────────────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
def login(body: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user by email and password.

    - Returns 401 if credentials are invalid.
    - Returns JWT token on success.
    """
    user = db.query(User).filter(User.email == body.email.lower().strip()).first()
    if not user or not pwd_context.verify(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token = create_access_token(user.id)
    logger.info("User logged in: %s (id=%d)", user.email, user.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


# ─── 3. Get Current User ────────────────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Return the profile of the currently authenticated user.
    Requires a valid JWT token in the Authorization header.
    """
    return UserOut.model_validate(current_user)
