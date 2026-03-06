from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.db.schemas import ReviewCreateRequest, ReviewResponse
from app.core.dependencies import get_current_customer, get_current_user
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse)
def create_review(
    review_data: ReviewCreateRequest,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Create a review for a completed order."""
    review_service = ReviewService(db)
    return review_service.create_review(current_user.id, review_data)


@router.get("/provider/{provider_id}", response_model=list[ReviewResponse])
def get_reviews_by_provider(
    provider_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reviews for a service provider."""
    review_service = ReviewService(db)
    return review_service.get_reviews_by_provider(provider_id)


@router.get("/order/{order_id}", response_model=ReviewResponse)
def get_review_by_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get review for a specific order."""
    review_service = ReviewService(db)
    return review_service.get_review_by_order(order_id)


@router.get("/provider/{provider_id}/stats")
def get_provider_rating_stats(
    provider_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get rating statistics for a service provider."""
    review_service = ReviewService(db)
    return review_service.get_provider_rating_stats(provider_id)

