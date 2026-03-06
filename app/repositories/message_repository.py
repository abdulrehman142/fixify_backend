from sqlalchemy.orm import Session
from app.db.models import Message
from typing import Optional, List


class MessageRepository:
    """Repository for Message database operations."""
    
    @staticmethod
    def create(
        db: Session,
        order_id: int,
        sender_id: int,
        sender_type: str,
        message_text: str
    ) -> Message:
        """Create a new message."""
        message = Message(
            order_id=order_id,
            sender_id=sender_id,
            sender_type=sender_type,
            message_text=message_text
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_by_order_id(db: Session, order_id: int) -> List[Message]:
        """Get all messages for an order, ordered by creation time."""
        return db.query(Message).filter(
            Message.order_id == order_id
        ).order_by(Message.created_at.asc()).all()
    
    @staticmethod
    def get_by_id(db: Session, message_id: int) -> Optional[Message]:
        """Get message by ID."""
        return db.query(Message).filter(Message.id == message_id).first()

