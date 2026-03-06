from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models import Review, Order
from app.db.schemas import ReviewCreateRequest, ReviewResponse
from app.repositories.review_repository import ReviewRepository
from app.repositories.order_repository import OrderRepository


class ReviewService:
    """Service for review operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository()
        self.order_repo = OrderRepository()
    
    def create_review(self, customer_id: int, request: ReviewCreateRequest) -> ReviewResponse:
        """Create a review for a completed order."""
        # Get order
        order = self.order_repo.get_by_id(self.db, request.order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if order belongs to customer
        if order.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to review this order"
            )
        
        # Check if order is completed
        if order.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only review completed orders"
            )
        
        # Check if review already exists
        existing_review = self.review_repo.get_by_order_id(self.db, request.order_id)
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Review already exists for this order"
            )
        
        if not order.service_provider_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order has no assigned service provider"
            )
        
        # Create review
        review = self.review_repo.create(
            db=self.db,
            order_id=request.order_id,
            customer_id=customer_id,
            service_provider_id=order.service_provider_id,
            rating=request.rating,
            comment=request.comment
        )
        
        return ReviewResponse.model_validate(review)
    
    def get_reviews_by_provider(self, provider_id: int) -> list[ReviewResponse]:
        """Get all reviews for a service provider."""
        reviews = self.review_repo.get_by_provider(self.db, provider_id)
        return [ReviewResponse.model_validate(review) for review in reviews]
    
    def get_review_by_order(self, order_id: int) -> ReviewResponse:
        """Get review for a specific order."""
        review = self.review_repo.get_by_order_id(self.db, order_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        return ReviewResponse.model_validate(review)
    
    def get_provider_rating_stats(self, provider_id: int) -> dict:
        """Get rating statistics for a service provider."""
        avg_rating = self.review_repo.get_average_rating(self.db, provider_id)
        rating_count = self.review_repo.get_rating_count(self.db, provider_id)
        
        return {
            "average_rating": round(avg_rating, 2),
            "total_reviews": rating_count
        }

