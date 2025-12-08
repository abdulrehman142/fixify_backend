from sqlalchemy.orm import Session
from db.models import Order
from typing import Optional, List, Union
from datetime import date, time
from db.schemas import OrderCreateRequest, OrderUpdateRequest


class OrderRepository:
    """Repository for Order database operations."""
    
    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID."""
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_by_order_number(db: Session, order_number: str) -> Optional[Order]:
        """Get order by order number."""
        return db.query(Order).filter(Order.order_number == order_number).first()
    
    @staticmethod
    def create(
        db: Session,
        order_number: str,
        customer_id: int,
        service_name: str,
        service_category: str,
        service_date: date,
        service_time: Union[time, str],
        address: str,
        total_amount: float,
        city: Optional[str] = None,
        postal_code: Optional[str] = None,
        special_instructions: Optional[str] = None
    ) -> Order:
        """Create a new order."""
        # Convert string time to time object if needed
        if isinstance(service_time, str):
            time_parts = service_time.split(":")
            if len(time_parts) >= 2:
                service_time = time(int(time_parts[0]), int(time_parts[1]))
            else:
                raise ValueError("Invalid time format")
        
        order = Order(
            order_number=order_number,
            customer_id=customer_id,
            service_name=service_name,
            service_category=service_category,
            service_date=service_date,
            service_time=service_time,
            address=address,
            city=city,
            postal_code=postal_code,
            total_amount=total_amount,
            special_instructions=special_instructions,
            status="pending"
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def update(
        db: Session,
        order_id: int,
        update_data: OrderUpdateRequest
    ) -> Optional[Order]:
        """Update order."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(order, key, value)
            db.commit()
            db.refresh(order)
        return order
    
    @staticmethod
    def assign_provider(
        db: Session,
        order_id: int,
        provider_id: int
    ) -> Optional[Order]:
        """Assign a service provider to an order."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.service_provider_id = provider_id
            order.status = "assigned"
            db.commit()
            db.refresh(order)
        return order
    
    @staticmethod
    def update_status(
        db: Session,
        order_id: int,
        status: str
    ) -> Optional[Order]:
        """Update order status."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = status
            db.commit()
            db.refresh(order)
        return order
    
    @staticmethod
    def get_by_customer(db: Session, customer_id: int) -> List[Order]:
        """Get all orders for a customer."""
        return db.query(Order).filter(Order.customer_id == customer_id).order_by(
            Order.created_at.desc()
        ).all()
    
    @staticmethod
    def get_by_provider(db: Session, provider_id: int) -> List[Order]:
        """Get all orders for a service provider."""
        return db.query(Order).filter(Order.service_provider_id == provider_id).order_by(
            Order.created_at.desc()
        ).all()
    
    @staticmethod
    def get_available(db: Session, service_category: Optional[str] = None) -> List[Order]:
        """Get all available (pending) orders, optionally filtered by service category."""
        query = db.query(Order).filter(Order.status == "pending")
        if service_category:
            query = query.filter(Order.service_category == service_category)
        return query.order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_all(db: Session) -> List[Order]:
        """Get all orders."""
        return db.query(Order).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_by_status(db: Session, status: str) -> List[Order]:
        """Get orders by status."""
        return db.query(Order).filter(Order.status == status).order_by(
            Order.created_at.desc()
        ).all()
    
    @staticmethod
    def delete(db: Session, order_id: int) -> bool:
        """Delete an order."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            db.delete(order)
            db.commit()
            return True
        return False

