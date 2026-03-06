from sqlalchemy.orm import Session
from app.db.models import User
from typing import Optional, List


class UserRepository:
    """Repository for User database operations."""
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def create(db: Session, username: str, email: str, password_hash: str, role: str) -> User:
        """Create a new user."""
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_token_version(db: Session, user: User) -> User:
        """Update user's token version to invalidate old tokens."""
        user.token_version += 1
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def exists_by_email_or_username(db: Session, email: str, username: str) -> bool:
        """Check if user exists by email or username."""
        return db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first() is not None
    
    @staticmethod
    def get_all_by_role(db: Session, role: str) -> List[User]:
        """Get all users by role."""
        return db.query(User).filter(User.role == role).all()
    
    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """Delete a user."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

