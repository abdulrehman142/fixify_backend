from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import ContactCreateRequest, ContactResponse
from services.contact_service import ContactService

router = APIRouter(prefix="/contact", tags=["Contact"])


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def submit_contact(
    contact_data: ContactCreateRequest,
    db: Session = Depends(get_db)
):
    """Submit a contact/complaint form (public endpoint)."""
    contact_service = ContactService(db)
    return contact_service.create_contact(contact_data)

