from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Decode JWT, validate, and return the SQLAlchemy User instance.
    Raises 401 on invalid/expired token or if user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise credentials_exception

    user_id = payload.get("id")
    token_version = payload.get("token_version")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if user.token_version != token_version:
        raise HTTPException(status_code=401, detail="Token invalidated. Login again.")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require core_admin or superadmin.
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

def require_service_provider(current_user: User = Depends(get_current_user)) -> User:
    """
    Require service_provider role.
    """
    if current_user.role != "service_provider":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Service provider privileges required")
    return current_user

def require_customer(current_user: User = Depends(get_current_user)) -> User:
    """
    Require customer role.
    """
    if current_user.role != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer privileges required")
    return current_user


def get_current_customer(current_user: User = Depends(require_customer)) -> User:
    """
    Get current customer user (alias for require_customer for clarity).
    """
    return current_user


def get_current_provider(current_user: User = Depends(require_service_provider)) -> User:
    """
    Get current service provider user (alias for require_service_provider for clarity).
    """
    return current_user
