from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from db.schemas import OrderResponse
from core.dependencies import get_current_user
from services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order details by ID."""
    order_service = OrderService(db)
    return order_service.get_order(order_id, current_user.id, current_user.role)


@router.get("", response_model=list[OrderResponse])
def list_orders(
    status_filter: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List orders with optional status filter (admin only for all orders)."""
    order_service = OrderService(db)
    
    # Admin can see all orders
    if current_user.role == "admin":
        if status_filter:
            from repositories.order_repository import OrderRepository
            order_repo = OrderRepository()
            orders = order_repo.get_by_status(db, status_filter)
            return [OrderResponse.model_validate(order) for order in orders]
        else:
            return order_service.get_all_orders()
    
    # Customers see their own orders
    elif current_user.role == "customer":
        return order_service.get_customer_orders(current_user.id)
    
    # Providers see their own orders
    elif current_user.role == "service_provider":
        return order_service.get_provider_orders(current_user.id)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

