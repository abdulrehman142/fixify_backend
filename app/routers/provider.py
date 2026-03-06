from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.db.schemas import ProviderResponse, ProviderProfileUpdate, OrderResponse, ProviderStatsResponse
from app.core.dependencies import get_current_provider
from app.services.provider_service import ProviderService
from app.services.order_service import OrderService

router = APIRouter(prefix="/provider", tags=["Service Provider"])


@router.get("/profile", response_model=ProviderResponse)
def get_profile(
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Get service provider profile."""
    provider_service = ProviderService(db)
    return provider_service.get_profile(current_user.id)


@router.put("/profile", response_model=ProviderResponse)
def update_profile(
    update_data: ProviderProfileUpdate,
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Update service provider profile."""
    provider_service = ProviderService(db)
    return provider_service.update_profile(current_user.id, update_data)


@router.get("/approval-status")
def get_approval_status(
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Get approval status for service provider."""
    provider_service = ProviderService(db)
    return provider_service.get_approval_status(current_user.id)


@router.get("/orders/available", response_model=list[OrderResponse])
def get_available_orders(
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Get available (pending) orders for service provider."""
    order_service = OrderService(db)
    return order_service.get_available_orders(current_user.id)


@router.post("/orders/{order_id}/pickup", response_model=OrderResponse)
def pickup_order(
    order_id: int,
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Service provider picks up an order."""
    order_service = OrderService(db)
    return order_service.pickup_order(order_id, current_user.id)


@router.post("/orders/{order_id}/complete", response_model=OrderResponse)
def complete_order(
    order_id: int,
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Service provider marks order as completed."""
    order_service = OrderService(db)
    return order_service.complete_order(order_id, current_user.id)


@router.get("/orders", response_model=list[OrderResponse])
def get_provider_orders(
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Get all orders for the current service provider."""
    order_service = OrderService(db)
    return order_service.get_provider_orders(current_user.id)


@router.get("/stats", response_model=ProviderStatsResponse)
def get_provider_stats(
    current_user: User = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Get statistics for the current service provider."""
    order_service = OrderService(db)
    stats = order_service.get_provider_stats(current_user.id)
    return ProviderStatsResponse(**stats)

