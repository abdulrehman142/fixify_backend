from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from db.models import Order
from db.schemas import OrderCreateRequest, OrderResponse, OrderUpdateRequest
from repositories.order_repository import OrderRepository
from repositories.provider_repository import ProviderRepository
from utils.order_number import generate_order_number
from utils.service_mapper import get_service_category
from services.provider_service import ProviderService


class OrderService:
    """Service for order operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository()
        self.provider_repo = ProviderRepository()
        self.provider_service = ProviderService(db)
    
    def create_order(self, customer_id: int, request: OrderCreateRequest) -> OrderResponse:
        """Create a new order with automatic service category detection."""
        order_number = generate_order_number(self.db)
        
        # Automatically determine service category from service name
        service_category = get_service_category(request.service_name)
        
        order = self.order_repo.create(
            db=self.db,
            order_number=order_number,
            customer_id=customer_id,
            service_name=request.service_name,
            service_category=service_category,
            service_date=request.service_date,
            service_time=request.service_time,
            address=request.address,
            total_amount=request.total_amount,
            city=request.city,
            postal_code=request.postal_code,
            special_instructions=request.special_instructions
        )
        
        return OrderResponse.model_validate(order)
    
    def get_order(self, order_id: int, user_id: int, user_role: str) -> OrderResponse:
        """Get order by ID with authorization check."""
        order = self.order_repo.get_by_id(self.db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check authorization
        if user_role == "customer" and order.customer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this order"
            )
        elif user_role == "service_provider":
            # Allow providers to see available (pending) orders
            if order.status == "pending":
                # Any provider can see pending orders
                pass
            else:
                # For non-pending orders, check if this provider is assigned
                provider = self.provider_repo.get_by_user_id(self.db, user_id)
                if not provider or order.service_provider_id != provider.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not authorized to view this order"
                    )
        
        return OrderResponse.model_validate(order)
    
    def get_customer_orders(self, customer_id: int) -> list[OrderResponse]:
        """Get all orders for a customer."""
        orders = self.order_repo.get_by_customer(self.db, customer_id)
        return [OrderResponse.model_validate(order) for order in orders]
    
    def get_provider_orders(self, provider_user_id: int) -> list[OrderResponse]:
        """Get all orders for a service provider."""
        provider = self.provider_repo.get_by_user_id(self.db, provider_user_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service provider not found"
            )
        
        orders = self.order_repo.get_by_provider(self.db, provider.id)
        return [OrderResponse.model_validate(order) for order in orders]
    
    def get_provider_stats(self, provider_user_id: int) -> dict:
        """Get statistics for a service provider."""
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        provider = self.provider_repo.get_by_user_id(self.db, provider_user_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service provider not found"
            )
        
        # Get all orders for this provider
        orders = self.order_repo.get_by_provider(self.db, provider.id)
        
        # Calculate basic stats
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.status == "completed"])
        pending_orders = len([o for o in orders if o.status == "pending"])
        assigned_orders = len([o for o in orders if o.status == "assigned"])
        in_progress_orders = len([o for o in orders if o.status == "in_progress"])
        
        # Calculate earnings (only from completed orders)
        total_earnings = sum(float(o.total_amount) for o in orders if o.status == "completed")
        
        # Get unique customers
        unique_customers = len(set(o.customer_id for o in orders))
        
        # Calculate average order value
        average_order_value = total_earnings / completed_orders if completed_orders > 0 else 0.0
        
        # Calculate monthly stats (last 12 months)
        monthly_stats = defaultdict(lambda: {"earnings": 0.0, "orders": 0})
        
        for order in orders:
            if order.status == "completed" and order.created_at:
                # Get month-year key
                order_date = order.created_at
                if isinstance(order_date, str):
                    order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                month_key = order_date.strftime("%Y-%m")
                monthly_stats[month_key]["earnings"] += float(order.total_amount)
                monthly_stats[month_key]["orders"] += 1
        
        # Convert to list sorted by month
        monthly_list = []
        for i in range(11, -1, -1):  # Last 12 months
            date = datetime.now() - timedelta(days=30 * i)
            month_key = date.strftime("%Y-%m")
            month_name = date.strftime("%B %Y")
            monthly_list.append({
                "month": month_name,
                "month_key": month_key,
                "earnings": monthly_stats[month_key]["earnings"],
                "orders": monthly_stats[month_key]["orders"]
            })
        
        return {
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "pending_orders": pending_orders,
            "assigned_orders": assigned_orders,
            "in_progress_orders": in_progress_orders,
            "total_earnings": round(total_earnings, 2),
            "unique_customers": unique_customers,
            "average_order_value": round(average_order_value, 2),
            "monthly_stats": monthly_list
        }
    
    def get_available_orders(self, provider_user_id: int) -> list[OrderResponse]:
        """Get available orders for a service provider, filtered by their service category."""
        # Check if provider is approved
        if not self.provider_service.is_approved(provider_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Service provider must be approved to view available orders"
            )
        
        # Get provider's service category
        provider = self.provider_repo.get_by_user_id(self.db, provider_user_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service provider not found"
            )
        
        # Get available orders filtered by provider's service category
        orders = self.order_repo.get_available(self.db, service_category=provider.service_category)
        return [OrderResponse.model_validate(order) for order in orders]
    
    def pickup_order(self, order_id: int, provider_user_id: int) -> OrderResponse:
        """Service provider picks up an order."""
        # Check if provider is approved
        if not self.provider_service.is_approved(provider_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Service provider must be approved to pick up orders"
            )
        
        # Get provider
        provider = self.provider_repo.get_by_user_id(self.db, provider_user_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service provider not found"
            )
        
        # Get order
        order = self.order_repo.get_by_id(self.db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if order.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not available for pickup"
            )
        
        # Check if order service category matches provider's service category
        if order.service_category != provider.service_category:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This order requires a {order.service_category} service provider. Your category is {provider.service_category}."
            )
        
        # Assign provider
        updated_order = self.order_repo.assign_provider(self.db, order_id, provider.id)
        if not updated_order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to assign provider"
            )
        
        return OrderResponse.model_validate(updated_order)
    
    def complete_order(self, order_id: int, provider_user_id: int) -> OrderResponse:
        """Service provider marks order as completed."""
        # Get provider
        provider = self.provider_repo.get_by_user_id(self.db, provider_user_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service provider not found"
            )
        
        # Get order
        order = self.order_repo.get_by_id(self.db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if order.service_provider_id != provider.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to complete this order"
            )
        
        if order.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is already completed"
            )
        
        # Update status
        updated_order = self.order_repo.update_status(self.db, order_id, "completed")
        if not updated_order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update order status"
            )
        
        return OrderResponse.model_validate(updated_order)
    
    def get_all_orders(self) -> list[OrderResponse]:
        """Get all orders (admin only)."""
        orders = self.order_repo.get_all(self.db)
        return [OrderResponse.model_validate(order) for order in orders]
    
    def delete_order(self, order_id: int, customer_id: int) -> None:
        """Delete an order (only pending orders can be deleted by customer)."""
        order = self.order_repo.get_by_id(self.db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check authorization - only the customer who created the order can delete it
        if order.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this order"
            )
        
        # Only pending orders can be deleted
        if order.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending orders can be deleted"
            )
        
        # Delete the order
        deleted = self.order_repo.delete(self.db, order_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete order"
            )
    
    def reschedule_order(self, order_id: int, customer_id: int, update_data: OrderUpdateRequest) -> OrderResponse:
        """Reschedule/update an order (only pending orders can be rescheduled by customer)."""
        order = self.order_repo.get_by_id(self.db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check authorization - only the customer who created the order can reschedule it
        if order.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to reschedule this order"
            )
        
        # Only pending orders can be rescheduled
        if order.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending orders can be rescheduled"
            )
        
        # Update the order
        updated_order = self.order_repo.update(self.db, order_id, update_data)
        if not updated_order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update order"
            )
        
        return OrderResponse.model_validate(updated_order)

