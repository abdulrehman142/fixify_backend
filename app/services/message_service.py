from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models import Message, Order, User
from app.db.schemas import MessageCreateRequest, MessageResponse
from app.repositories.message_repository import MessageRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.provider_repository import ProviderRepository


class MessageService:
    """Service for message operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.message_repo = MessageRepository()
        self.order_repo = OrderRepository()
        self.provider_repo = ProviderRepository()
    
    def send_message(self, user_id: int, user_role: str, request: MessageCreateRequest) -> MessageResponse:
        """Send a message for an order."""
        # Get order
        order = self.order_repo.get_by_id(self.db, request.order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Determine sender type
        if user_role == "customer":
            # Customer can only message if order is assigned or completed
            if order.status == "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot message for pending orders. Order must be assigned first."
                )
            # Verify customer owns the order
            if order.customer_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to message for this order"
                )
            sender_type = "customer"
        elif user_role == "service_provider":
            # Provider can only message if order is assigned or completed
            if order.status == "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot message for pending orders. Order must be assigned first."
                )
            # Verify provider is assigned to the order
            provider = self.provider_repo.get_by_user_id(self.db, user_id)
            if not provider or order.service_provider_id != provider.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to message for this order"
                )
            sender_type = "service_provider"
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers and service providers can send messages"
            )
        
        # Create message
        message = self.message_repo.create(
            db=self.db,
            order_id=request.order_id,
            sender_id=user_id,
            sender_type=sender_type,
            message_text=request.message_text
        )
        
        # Get sender username for response
        sender = self.db.query(User).filter(User.id == user_id).first()
        sender_username = sender.username if sender else None
        
        response = MessageResponse.model_validate(message)
        response.sender_username = sender_username
        return response
    
    def get_messages_for_order(self, order_id: int, user_id: int, user_role: str) -> list[MessageResponse]:
        """Get all messages for an order with authorization check."""
        # Get order
        order = self.order_repo.get_by_id(self.db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check authorization
        if user_role == "customer":
            if order.customer_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view messages for this order"
                )
        elif user_role == "service_provider":
            provider = self.provider_repo.get_by_user_id(self.db, user_id)
            if not provider or order.service_provider_id != provider.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view messages for this order"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers and service providers can view messages"
            )
        
        # Get messages
        messages = self.message_repo.get_by_order_id(self.db, order_id)
        
        # Get sender usernames
        result = []
        for message in messages:
            sender = self.db.query(User).filter(User.id == message.sender_id).first()
            msg_response = MessageResponse.model_validate(message)
            msg_response.sender_username = sender.username if sender else None
            result.append(msg_response)
        
        return result

