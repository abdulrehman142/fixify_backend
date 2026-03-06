from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models import User
from app.db.schemas import CustomerRegisterRequest, ProviderRegisterRequest, LoginRequest, TokenResponse
from app.repositories.user_repository import UserRepository
from app.repositories.provider_repository import ProviderRepository
from app.utils.hashing import hash_password, verify_password
from app.core.security import create_access_token


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository()
        self.provider_repo = ProviderRepository()
    
    def register_customer(self, request: CustomerRegisterRequest) -> User:
        """Register a new customer."""
        # Check if user already exists
        if self.user_repo.exists_by_email_or_username(self.db, request.email, request.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists"
            )
        
        # Create user
        user = self.user_repo.create(
            db=self.db,
            username=request.name,
            email=request.email,
            password_hash=hash_password(request.password),
            role="customer"
        )
        
        return user
    
    def register_provider(self, request: ProviderRegisterRequest) -> User:
        """Register a new service provider."""
        # Check if user already exists
        if self.user_repo.exists_by_email_or_username(self.db, request.email, request.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists"
            )
        
        # Create user
        user = self.user_repo.create(
            db=self.db,
            username=request.username,
            email=request.email,
            password_hash=hash_password(request.password),
            role="service_provider"
        )
        
        # Create service provider profile
        self.provider_repo.create(
            db=self.db,
            user_id=user.id,
            service_category=request.service_category,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            city=request.city,
            business_name=request.business_name,
            experience_years=request.experience_years,
            hourly_rate=request.hourly_rate,
            bio=request.bio,
            address=request.address
        )
        
        return user
    
    def login(self, request: LoginRequest) -> TokenResponse:
        """Authenticate user and return JWT token."""
        # Try to find user by email
        user = self.user_repo.get_by_email(self.db, request.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token({
            "id": user.id,
            "role": user.role,
            "username": user.username,
            "token_version": user.token_version
        })
        
        return TokenResponse(access_token=access_token)

