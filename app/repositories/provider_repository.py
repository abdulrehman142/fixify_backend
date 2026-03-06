from sqlalchemy.orm import Session
from app.db.models import ServiceProvider, User
from typing import Optional, List
from app.db.schemas import ProviderProfileUpdate


class ProviderRepository:
    """Repository for ServiceProvider database operations."""
    
    @staticmethod
    def get_by_id(db: Session, provider_id: int) -> Optional[ServiceProvider]:
        """Get service provider by ID."""
        return db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    
    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[ServiceProvider]:
        """Get service provider by user ID."""
        return db.query(ServiceProvider).filter(ServiceProvider.user_id == user_id).first()
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        service_category: str,
        first_name: str,
        last_name: str,
        phone: str,
        city: str,
        business_name: Optional[str] = None,
        experience_years: Optional[int] = None,
        hourly_rate: Optional[float] = None,
        bio: Optional[str] = None,
        address: Optional[str] = None
    ) -> ServiceProvider:
        """Create a new service provider."""
        provider = ServiceProvider(
            user_id=user_id,
            service_category=service_category,
            approval_status="pending",
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            business_name=business_name,
            experience_years=experience_years,
            hourly_rate=hourly_rate,
            bio=bio,
            city=city,
            address=address
        )
        db.add(provider)
        db.commit()
        db.refresh(provider)
        return provider
    
    @staticmethod
    def update_approval_status(
        db: Session,
        provider_id: int,
        status: str
    ) -> Optional[ServiceProvider]:
        """Update provider approval status."""
        provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
        if provider:
            provider.approval_status = status
            db.commit()
            db.refresh(provider)
        return provider
    
    @staticmethod
    def update_profile(
        db: Session,
        provider_id: int,
        update_data: ProviderProfileUpdate
    ) -> Optional[ServiceProvider]:
        """Update provider profile."""
        provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
        if provider:
            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(provider, key, value)
            db.commit()
            db.refresh(provider)
        return provider
    
    @staticmethod
    def get_pending(db: Session) -> List[ServiceProvider]:
        """Get all pending service providers."""
        return db.query(ServiceProvider).filter(
            ServiceProvider.approval_status == "pending"
        ).all()
    
    @staticmethod
    def get_all(db: Session) -> List[ServiceProvider]:
        """Get all service providers."""
        return db.query(ServiceProvider).all()
    
    @staticmethod
    def get_approved(db: Session) -> List[ServiceProvider]:
        """Get all approved service providers."""
        return db.query(ServiceProvider).filter(
            ServiceProvider.approval_status == "approved"
        ).all()
    
    @staticmethod
    def get_by_category(db: Session, category: str) -> List[ServiceProvider]:
        """Get approved providers by service category."""
        return db.query(ServiceProvider).filter(
            ServiceProvider.service_category == category,
            ServiceProvider.approval_status == "approved"
        ).all()
    
    @staticmethod
    def delete(db: Session, provider_id: int) -> bool:
        """Delete a service provider."""
        provider = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
        if provider:
            db.delete(provider)
            db.commit()
            return True
        return False

