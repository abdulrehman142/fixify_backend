from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from utils.hashing import hash_password
from core.dependencies import require_admin
from db.schemas import (
    CreateUserRequest, UpdateUserRequest, ProviderListResponse, 
    OrderListResponse, StatsResponse, ProviderApprovalRequest,
    CustomerListItem, ProviderStatsDetail, CustomerStatsDetail, ContactResponse
)
from repositories.provider_repository import ProviderRepository
from repositories.order_repository import OrderRepository
from repositories.user_repository import UserRepository
from services.order_service import OrderService
from services.contact_service import ContactService

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================
# SUPERADMIN ONLY ROUTE
# Create CORE ADMINS
# ============================

@router.post("/create_service_provider")
def create_core_admin(
    payload: CreateUserRequest,
    current=Depends(require_admin),
    db: Session = Depends(get_db)
):

    exists = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()

    if exists:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="service_provider",
        token_version=0
    )

    db.add(user)
    db.commit()

    return {"status": "service_provider_created"}


# ============================
# CORE_ADMIN + SUPERADMIN ROUTE
# Create SUBADMINS
# ============================

@router.post("/create_customer")
def create_subadmin(
    payload: CreateUserRequest,
    db: Session = Depends(get_db)
):

    exists = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()

    if exists:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="customer",
        token_version=0
    )

    db.add(user)
    db.commit()

    return {"status": "customer_created"}


# ============================
# GET ADMINS
# ============================

@router.get("/list")
def list_admins(
    current=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    - admin: get service_provider + customer
    """
    if current.role == "admin":
        users = db.query(User).filter(User.role.in_(["service_provider", "customer"])).all()

    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role
        }
        for u in users
    ]


# ==================== Provider Management ====================

@router.get("/providers/pending", response_model=list[ProviderListResponse])
def get_pending_providers(
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all pending service providers."""
    provider_repo = ProviderRepository()
    providers = provider_repo.get_pending(db)
    
    result = []
    for provider in providers:
        user = db.query(User).filter(User.id == provider.user_id).first()
        result.append(ProviderListResponse(
            id=provider.id,
            user_id=provider.user_id,
            name=f"{provider.first_name} {provider.last_name}",
            email=user.email if user else "",
            phone=provider.phone,
            service_category=provider.service_category,
            business_name=provider.business_name,
            experience_years=provider.experience_years,
            city=provider.city,
            approval_status=provider.approval_status,
            applied_date=provider.created_at
        ))
    
    return result


@router.post("/providers/{provider_id}/approve")
def approve_provider(
    provider_id: int,
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve a service provider."""
    provider_repo = ProviderRepository()
    provider = provider_repo.update_approval_status(db, provider_id, "approved")
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service provider not found"
        )
    
    return {"status": "approved", "provider_id": provider_id}


@router.post("/providers/{provider_id}/reject")
def reject_provider(
    provider_id: int,
    request: ProviderApprovalRequest,
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reject a service provider."""
    provider_repo = ProviderRepository()
    provider = provider_repo.update_approval_status(db, provider_id, "rejected")
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service provider not found"
        )
    
    return {
        "status": "rejected",
        "provider_id": provider_id,
        "reason": request.rejection_reason
    }


@router.get("/providers", response_model=list[ProviderListResponse])
def get_all_providers(
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all service providers."""
    provider_repo = ProviderRepository()
    providers = provider_repo.get_all(db)
    
    result = []
    for provider in providers:
        user = db.query(User).filter(User.id == provider.user_id).first()
        result.append(ProviderListResponse(
            id=provider.id,
            user_id=provider.user_id,
            name=f"{provider.first_name} {provider.last_name}",
            email=user.email if user else "",
            phone=provider.phone,
            service_category=provider.service_category,
            business_name=provider.business_name,
            experience_years=provider.experience_years,
            city=provider.city,
            approval_status=provider.approval_status,
            applied_date=provider.created_at
        ))
    
    return result


# ==================== Order Management ====================

@router.get("/orders", response_model=list[OrderListResponse])
def get_all_orders(
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all orders."""
    order_service = OrderService(db)
    orders = order_service.get_all_orders()
    
    result = []
    for order in orders:
        provider_name = None
        if order.service_provider:
            provider_name = f"{order.service_provider.first_name} {order.service_provider.last_name}"
        
        result.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            customer_name=order.customer.username if order.customer else "",
            service_name=order.service_name,
            service_category=order.service_category,
            service_date=order.service_date,
            total_amount=order.total_amount,
            status=order.status,
            provider_name=provider_name
        ))
    
    return result


# ==================== Statistics ====================

@router.get("/stats", response_model=StatsResponse)
def get_statistics(
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics."""
    provider_repo = ProviderRepository()
    order_repo = OrderRepository()
    user_repo = UserRepository()
    
    all_providers = provider_repo.get_all(db)
    total_providers = len(all_providers)
    approved_providers = len([p for p in all_providers if p.approval_status == "approved"])
    pending_providers = len([p for p in all_providers if p.approval_status == "pending"])
    rejected_providers = len([p for p in all_providers if p.approval_status == "rejected"])
    
    all_orders = order_repo.get_all(db)
    total_orders = len(all_orders)
    pending_orders = len([o for o in all_orders if o.status == "pending"])
    assigned_orders = len([o for o in all_orders if o.status == "assigned"])
    in_progress_orders = len([o for o in all_orders if o.status == "in_progress"])
    completed_orders = len([o for o in all_orders if o.status == "completed"])
    
    # Calculate total earnings from completed orders
    total_earnings = sum(float(o.total_amount) for o in all_orders if o.status == "completed")
    
    # Calculate average order value
    average_order_value = total_earnings / completed_orders if completed_orders > 0 else 0.0
    
    # Get total customers
    all_customers = user_repo.get_all_by_role(db, "customer")
    total_customers = len(all_customers)
    
    return StatsResponse(
        total_providers=total_providers,
        approved_providers=approved_providers,
        pending_providers=pending_providers,
        rejected_providers=rejected_providers,
        total_orders=total_orders,
        pending_orders=pending_orders,
        assigned_orders=assigned_orders,
        completed_orders=completed_orders,
        total_customers=total_customers,
        total_earnings=round(total_earnings, 2),
        average_order_value=round(average_order_value, 2),
        in_progress_orders=in_progress_orders
    )


# ==================== Customer Management ====================

@router.get("/customers", response_model=list[CustomerListItem])
def get_all_customers(
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all customers with their order statistics."""
    user_repo = UserRepository()
    order_repo = OrderRepository()
    
    customers = user_repo.get_all_by_role(db, "customer")
    result = []
    
    for customer in customers:
        # Get customer's orders
        orders = order_repo.get_by_customer(db, customer.id)
        total_orders = len(orders)
        total_spent = sum(float(o.total_amount) for o in orders if o.status == "completed")
        
        result.append(CustomerListItem(
            id=customer.id,
            username=customer.username,
            email=customer.email,
            created_at=customer.created_at,
            total_orders=total_orders,
            total_spent=round(total_spent, 2)
        ))
    
    return result


@router.get("/customers/{customer_id}/stats", response_model=CustomerStatsDetail)
def get_customer_stats(
    customer_id: int,
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific customer."""
    user_repo = UserRepository()
    order_repo = OrderRepository()
    
    customer = user_repo.get_by_id(db, customer_id)
    if not customer or customer.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    orders = order_repo.get_by_customer(db, customer_id)
    total_orders = len(orders)
    completed_orders = len([o for o in orders if o.status == "completed"])
    pending_orders = len([o for o in orders if o.status == "pending"])
    assigned_orders = len([o for o in orders if o.status == "assigned"])
    in_progress_orders = len([o for o in orders if o.status == "in_progress"])
    
    total_spent = sum(float(o.total_amount) for o in orders if o.status == "completed")
    average_order_value = total_spent / completed_orders if completed_orders > 0 else 0.0
    
    return CustomerStatsDetail(
        total_orders=total_orders,
        completed_orders=completed_orders,
        pending_orders=pending_orders,
        assigned_orders=assigned_orders,
        in_progress_orders=in_progress_orders,
        total_spent=round(total_spent, 2),
        average_order_value=round(average_order_value, 2)
    )


@router.get("/providers/{provider_id}/stats", response_model=ProviderStatsDetail)
def get_provider_stats(
    provider_id: int,
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific service provider."""
    order_service = OrderService(db)
    provider_repo = ProviderRepository()
    
    provider = provider_repo.get_by_id(db, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service provider not found"
        )
    
    stats = order_service.get_provider_stats(provider.user_id)
    return ProviderStatsDetail(**stats)


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(
    provider_id: int,
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a service provider and their associated user account."""
    provider_repo = ProviderRepository()
    user_repo = UserRepository()
    
    provider = provider_repo.get_by_id(db, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service provider not found"
        )
    
    # Delete provider record
    provider_repo.delete(db, provider_id)
    
    # Delete associated user account
    user_repo.delete(db, provider.user_id)
    
    return None


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a customer and their associated data."""
    user_repo = UserRepository()
    order_repo = OrderRepository()
    
    customer = user_repo.get_by_id(db, customer_id)
    if not customer or customer.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Delete all orders associated with this customer
    orders = order_repo.get_by_customer(db, customer_id)
    for order in orders:
        order_repo.delete(db, order.id)
    
    # Delete user account
    deleted = user_repo.delete(db, customer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete customer"
        )
    
    return None


# ==================== Contact Messages ====================

@router.get("/contacts", response_model=list[ContactResponse])
def get_all_contacts(
    current: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all contact/complaint messages from customers."""
    contact_service = ContactService(db)
    return contact_service.get_all_contacts()

