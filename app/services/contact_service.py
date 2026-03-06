from sqlalchemy.orm import Session
from app.db.models import Contact
from app.db.schemas import ContactCreateRequest, ContactResponse
from app.repositories.contact_repository import ContactRepository


class ContactService:
    """Service for contact/complaint operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.contact_repo = ContactRepository()
    
    def create_contact(self, request: ContactCreateRequest) -> ContactResponse:
        """Create a contact/complaint submission."""
        contact = self.contact_repo.create(
            db=self.db,
            name=request.name,
            email=request.email,
            message=request.message
        )
        
        return ContactResponse.model_validate(contact)
    
    def get_all_contacts(self) -> list[ContactResponse]:
        """Get all contact submissions."""
        contacts = self.contact_repo.get_all(self.db)
        return [ContactResponse.model_validate(contact) for contact in contacts]

