from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from db.schemas import MessageCreateRequest, MessageResponse
from core.dependencies import get_current_user, get_current_customer, get_current_provider
from services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("", response_model=MessageResponse)
def send_message(
    message_data: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message for an order. Available for customers and service providers."""
    if current_user.role not in ["customer", "service_provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers and service providers can send messages"
        )
    
    message_service = MessageService(db)
    return message_service.send_message(current_user.id, current_user.role, message_data)


@router.get("/order/{order_id}", response_model=list[MessageResponse])
def get_messages(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for an order. Available for customers and service providers."""
    if current_user.role not in ["customer", "service_provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers and service providers can view messages"
        )
    
    message_service = MessageService(db)
    return message_service.get_messages_for_order(order_id, current_user.id, current_user.role)

