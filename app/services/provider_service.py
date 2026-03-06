from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models import ServiceProvider
from app.db.schemas import ProviderResponse, ProviderProfileUpdate
from app.repositories.provider_repository import ProviderRepository
from app.repositories.user_repository import UserRepository


class ProviderService:
    """Service for service provider operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.provider_repo = ProviderRepository()
        self.user_repo = UserRepository()
    
    def get_profile(self, user_id: int) -> ProviderResponse:
        """Get service provider profile."""
        provider = self.provider_repo.get_by_user_id(self.db, user_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service provider profile not found"
            )
        
        # Load user relationship
        provider.user = self.user_repo.get_by_id(self.db, user_id)
        return ProviderResponse.model_validate(provider)
    
    def update_profile(self, user_id: int, update_data: ProviderProfileUpdate) -> ProviderResponse:
        """Update service provider profile."""
        provider = self.provider_repo.get_by_user_id(self.db, user_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service provider profile not found"
            )
        
        updated_provider = self.provider_repo.update_profile(self.db, provider.id, update_data)
        if not updated_provider:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        # Load user relationship
        updated_provider.user = self.user_repo.get_by_id(self.db, user_id)
        return ProviderResponse.model_validate(updated_provider)
    
    def get_approval_status(self, user_id: int) -> dict:
        """Get approval status for service provider."""
        provider = self.provider_repo.get_by_user_id(self.db, user_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service provider profile not found"
            )
        
        return {
            "is_approved": provider.approval_status == "approved",
            "status": provider.approval_status
        }
    
    def is_approved(self, user_id: int) -> bool:
        """Check if service provider is approved."""
        provider = self.provider_repo.get_by_user_id(self.db, user_id)
        if not provider:
            return False
        return provider.approval_status == "approved"

