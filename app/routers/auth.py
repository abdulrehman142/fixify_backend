from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from db.schemas import (
    LoginRequest, TokenResponse, CustomerRegisterRequest, 
    ProviderRegisterRequest, CustomerResponse, ProviderResponse
)
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint - supports email-based authentication."""
    auth_service = AuthService(db)
    return auth_service.login(payload)


@router.post("/register", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def register_customer(payload: CustomerRegisterRequest, db: Session = Depends(get_db)):
    """Register a new customer."""
    auth_service = AuthService(db)
    user = auth_service.register_customer(payload)
    return CustomerResponse.model_validate(user)


@router.post("/register-provider", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
def register_provider(payload: ProviderRegisterRequest, db: Session = Depends(get_db)):
    """Register a new service provider (pending approval)."""
    auth_service = AuthService(db)
    user = auth_service.register_provider(payload)
    
    # Get the provider profile
    from repositories.provider_repository import ProviderRepository
    provider_repo = ProviderRepository()
    provider = provider_repo.get_by_user_id(db, user.id)
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create provider profile"
        )
    
    provider.user = user
    return ProviderResponse.model_validate(provider)
