from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal

# ==================== Auth Schemas ====================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str

class UpdateUserRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None

# ==================== Customer Schemas ====================

class CustomerRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)

class CustomerResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustomerProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

# ==================== Provider Schemas ====================

class ProviderRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=6)
    service_category: str = Field(..., pattern="^(cleaner|electrician|plumber|mechanic|mover|technician|painter|gardener|carpenter)$")
    first_name: str
    last_name: str
    phone: str
    business_name: Optional[str] = None
    experience_years: Optional[int] = None
    hourly_rate: Optional[Decimal] = None
    bio: Optional[str] = None
    city: str
    address: Optional[str] = None

class ProviderResponse(BaseModel):
    id: int
    user_id: int
    service_category: str
    approval_status: str
    first_name: str
    last_name: str
    phone: str
    business_name: Optional[str]
    experience_years: Optional[int]
    hourly_rate: Optional[Decimal]
    bio: Optional[str]
    city: str
    address: Optional[str]
    created_at: datetime
    user: Optional[CustomerResponse] = None
    
    class Config:
        from_attributes = True

class ProviderProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    business_name: Optional[str] = None
    experience_years: Optional[int] = None
    hourly_rate: Optional[Decimal] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None

class ProviderApprovalRequest(BaseModel):
    approval_status: str = Field(..., pattern="^(approved|rejected)$")
    rejection_reason: Optional[str] = None

# ==================== Order Schemas ====================

class OrderCreateRequest(BaseModel):
    service_name: str
    service_date: date
    service_time: time
    address: str
    city: Optional[str] = None
    postal_code: Optional[str] = None
    total_amount: Decimal
    special_instructions: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    service_provider_id: Optional[int]
    service_name: str
    service_category: str
    service_date: date
    service_time: time
    address: str
    city: Optional[str]
    postal_code: Optional[str]
    total_amount: Decimal
    special_instructions: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    customer: Optional[CustomerResponse] = None
    service_provider: Optional[ProviderResponse] = None
    
    class Config:
        from_attributes = True

class OrderUpdateRequest(BaseModel):
    service_date: Optional[date] = None
    service_time: Optional[time] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    special_instructions: Optional[str] = None

# ==================== Review Schemas ====================

class ReviewCreateRequest(BaseModel):
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    order_id: int
    customer_id: int
    service_provider_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    customer: Optional[CustomerResponse] = None
    
    class Config:
        from_attributes = True

# ==================== Contact Schemas ====================

class ContactCreateRequest(BaseModel):
    name: str
    email: EmailStr
    message: str = Field(..., min_length=10)

class ContactResponse(BaseModel):
    id: int
    name: str
    email: str
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Message Schemas ====================

class MessageCreateRequest(BaseModel):
    order_id: int
    message_text: str = Field(..., min_length=1, max_length=1000)

class MessageResponse(BaseModel):
    id: int
    order_id: int
    sender_id: int
    sender_type: str
    message_text: str
    created_at: datetime
    sender_username: Optional[str] = None
    
    class Config:
        from_attributes = True

# ==================== Admin Schemas ====================

class ProviderListResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    phone: str
    service_category: str
    business_name: Optional[str]
    experience_years: Optional[int]
    city: str
    approval_status: str
    applied_date: datetime
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    id: int
    order_number: str
    customer_name: str
    service_name: str
    service_category: str
    service_date: date
    total_amount: Decimal
    status: str
    provider_name: Optional[str]
    
    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total_providers: int
    approved_providers: int
    pending_providers: int
    rejected_providers: int
    total_orders: int
    pending_orders: int
    assigned_orders: int
    completed_orders: int
    total_customers: int
    total_earnings: float
    average_order_value: float
    in_progress_orders: int

class CustomerListItem(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    total_orders: int
    total_spent: float
    
    class Config:
        from_attributes = True

class ProviderStatsDetail(BaseModel):
    total_orders: int
    completed_orders: int
    pending_orders: int
    assigned_orders: int
    in_progress_orders: int
    total_earnings: float
    unique_customers: int
    average_order_value: float

class CustomerStatsDetail(BaseModel):
    total_orders: int
    completed_orders: int
    pending_orders: int
    assigned_orders: int
    in_progress_orders: int
    total_spent: float
    average_order_value: float

class ProviderStatsResponse(BaseModel):
    total_orders: int
    completed_orders: int
    pending_orders: int
    assigned_orders: int
    in_progress_orders: int
    total_earnings: float
    unique_customers: int
    average_order_value: float
    monthly_stats: list[dict]  # List of monthly stats with earnings and order counts