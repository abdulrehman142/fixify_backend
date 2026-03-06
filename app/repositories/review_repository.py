from sqlalchemy.orm import Session
from app.db.models import Review
from typing import Optional, List
from app.db.schemas import ReviewCreateRequest


class ReviewRepository:
    """Repository for Review database operations."""
    
    @staticmethod
    def get_by_id(db: Session, review_id: int) -> Optional[Review]:
        """Get review by ID."""
        return db.query(Review).filter(Review.id == review_id).first()
    
    @staticmethod
    def get_by_order_id(db: Session, order_id: int) -> Optional[Review]:
        """Get review by order ID."""
        return db.query(Review).filter(Review.order_id == order_id).first()
    
    @staticmethod
    def create(
        db: Session,
        order_id: int,
        customer_id: int,
        service_provider_id: int,
        rating: int,
        comment: Optional[str] = None
    ) -> Review:
        """Create a new review."""
        review = Review(
            order_id=order_id,
            customer_id=customer_id,
            service_provider_id=service_provider_id,
            rating=rating,
            comment=comment
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
    
    @staticmethod
    def get_by_provider(db: Session, provider_id: int) -> List[Review]:
        """Get all reviews for a service provider."""
        return db.query(Review).filter(
            Review.service_provider_id == provider_id
        ).order_by(Review.created_at.desc()).all()
    
    @staticmethod
    def get_average_rating(db: Session, provider_id: int) -> float:
        """Get average rating for a service provider."""
        from sqlalchemy import func
        result = db.query(func.avg(Review.rating)).filter(
            Review.service_provider_id == provider_id
        ).scalar()
        return float(result) if result else 0.0
    
    @staticmethod
    def get_rating_count(db: Session, provider_id: int) -> int:
        """Get total number of reviews for a service provider."""
        return db.query(Review).filter(Review.service_provider_id == provider_id).count()

