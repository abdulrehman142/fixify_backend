from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models import User
from app.db.schemas import CustomerProfileUpdate, CustomerResponse
from app.repositories.user_repository import UserRepository


class CustomerService:
    """Service for customer operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository()
    
    def get_profile(self, user_id: int) -> CustomerResponse:
        """Get customer profile."""
        user = self.user_repo.get_by_id(self.db, user_id)
        if not user or user.role != "customer":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return CustomerResponse.model_validate(user)
    
    def update_profile(self, user_id: int, update_data: CustomerProfileUpdate) -> CustomerResponse:
        """Update customer profile."""
        user = self.user_repo.get_by_id(self.db, user_id)
        if not user or user.role != "customer":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Check for email conflicts
        if "email" in update_dict:
            existing_user = self.user_repo.get_by_email(self.db, update_dict["email"])
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use"
                )
        
        # Check for username conflicts
        if "username" in update_dict:
            existing_user = self.user_repo.get_by_username(self.db, update_dict["username"])
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already in use"
                )
        
        # Update user
        for key, value in update_dict.items():
            setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return CustomerResponse.model_validate(user)

