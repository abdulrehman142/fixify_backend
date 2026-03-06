from sqlalchemy.orm import Session
from app.db.models import Contact
from typing import List


class ContactRepository:
    """Repository for Contact database operations."""
    
    @staticmethod
    def create(
        db: Session,
        name: str,
        email: str,
        message: str
    ) -> Contact:
        """Create a new contact submission."""
        contact = Contact(
            name=name,
            email=email,
            message=message
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact
    
    @staticmethod
    def get_all(db: Session) -> List[Contact]:
        """Get all contact submissions."""
        return db.query(Contact).order_by(Contact.created_at.desc()).all()

