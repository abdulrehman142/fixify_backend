from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from db.schemas import (
    CustomerResponse, CustomerProfileUpdate, 
    OrderCreateRequest, OrderResponse, OrderUpdateRequest
)
from core.dependencies import get_current_customer
from services.customer_service import CustomerService
from services.order_service import OrderService

router = APIRouter(prefix="/customer", tags=["Customer"])


@router.get("/profile", response_model=CustomerResponse)
def get_profile(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Get customer profile."""
    customer_service = CustomerService(db)
    return customer_service.get_profile(current_user.id)


@router.put("/profile", response_model=CustomerResponse)
def update_profile(
    update_data: CustomerProfileUpdate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Update customer profile."""
    customer_service = CustomerService(db)
    return customer_service.update_profile(current_user.id, update_data)


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreateRequest,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Create a new order."""
    order_service = OrderService(db)
    return order_service.create_order(current_user.id, order_data)


@router.get("/orders", response_model=list[OrderResponse])
def get_orders(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Get all orders for the current customer."""
    order_service = OrderService(db)
    return order_service.get_customer_orders(current_user.id)


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Delete a pending order (only pending orders can be deleted)."""
    order_service = OrderService(db)
    order_service.delete_order(order_id, current_user.id)
    return None


@router.put("/orders/{order_id}", response_model=OrderResponse)
def reschedule_order(
    order_id: int,
    update_data: OrderUpdateRequest,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Reschedule/update a pending order (only pending orders can be rescheduled)."""
    order_service = OrderService(db)
    return order_service.reschedule_order(order_id, current_user.id, update_data)

