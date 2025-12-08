# SOLID Principles & OOP Concepts Guide

## Table of Contents
1. [Introduction](#introduction)
2. [OOP Core Concepts](#oop-core-concepts)
3. [SOLID Principles](#solid-principles)
4. [Implementation in Fixify Backend](#implementation-in-fixify-backend)
5. [Best Practices](#best-practices)

---

## Introduction

**SOLID** is an acronym representing five design principles aimed at making software more understandable, flexible, and maintainable. Combined with Object-Oriented Programming (OOP) concepts, these principles create robust, scalable systems.

### Why SOLID Matters?
- ✅ Easier to understand and maintain code
- ✅ Reduces code complexity and duplication
- ✅ Improves testability
- ✅ Facilitates code reusability
- ✅ Reduces bug-prone changes

---

## OOP Core Concepts

### 1. **Encapsulation**
Bundling data and methods that operate on data into a single unit (class), hiding internal implementation details.

**Example from Fixify:**
```python
class UserRepository:
    """Repository for User database operations."""
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID - hides SQL query complexity."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create(db: Session, username: str, email: str, password_hash: str, role: str) -> User:
        """Create user - encapsulates creation logic."""
        user = User(username=username, email=email, password_hash=password_hash, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
```

**Benefits:**
- Internal details are hidden from external callers
- Changes to implementation don't affect external code
- Controlled access to object state

---

### 2. **Abstraction**
Hiding complex implementation details and exposing only essential features.

**Example from Fixify:**
```python
class OrderService:
    """Service abstracts order operations."""
    
    def create_order(self, customer_id: int, request: OrderCreateRequest) -> OrderResponse:
        """Customers don't need to know how order numbers are generated or categories mapped."""
        order_number = generate_order_number(self.db)  # Hidden complexity
        service_category = get_service_category(request.service_name)  # Abstracted logic
        
        order = self.order_repo.create(db=self.db, ...)
        return OrderResponse.model_validate(order)
```

**Benefits:**
- Reduces cognitive load for users of the class
- Implementation can change without affecting interface
- Cleaner, more intuitive API

---

### 3. **Inheritance**
Deriving new classes from existing ones, enabling code reuse and establishing relationships.

**Example from Fixify:**
```python
# Base model with common fields
class Base:
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

# ServiceProvider inherits from Base
class ServiceProvider(Base):
    __tablename__ = "service_providers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    # Additional specialized fields
    user_id = Column(BigInteger, ForeignKey("users.id"))
```

**Benefits:**
- Code reusability
- Establishes "is-a" relationships
- Shared functionality in parent classes

---

### 4. **Polymorphism**
Objects of different classes can be treated through the same interface, with each class implementing methods differently.

**Example from Fixify:**
```python
# Different user types with role-based behavior
class User(Base):
    role = Column(Enum("admin", "service_provider", "customer"))

# Routers treat users polymorphically
def get_orders(current_user: User = Depends(get_current_user)):
    """Same method handles different user types differently."""
    if current_user.role == "admin":
        return order_service.get_all_orders()
    elif current_user.role == "customer":
        return order_service.get_customer_orders(current_user.id)
    elif current_user.role == "service_provider":
        return order_service.get_provider_orders(current_user.id)
```

**Benefits:**
- Flexible code that adapts to object types
- Reduces conditional logic
- Extensible for new types

---

## SOLID Principles

### **S - Single Responsibility Principle**

**Definition:** A class or module should have only one reason to change, meaning it should have only one job or responsibility.

**Good Example from Fixify:**
```python
# UserRepository - Only handles User database operations
class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

# AuthService - Only handles authentication logic
class AuthService:
    def login(self, request: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_email(self.db, request.email)
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401)
        return TokenResponse(access_token=create_access_token(...))

# Routers - Only handle HTTP routing
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return auth_service.login(payload)
```

**Violations to Avoid:**
```python
# ❌ BAD: Multiple responsibilities
class UserController:
    def create_user(self):
        # 1. Validates input
        # 2. Hashes password
        # 3. Queries database
        # 4. Sends emails
        # 5. Logs events
        pass
```

**Benefits:**
- Easier to test individual components
- Code is more modular and reusable
- Changes are localized to specific classes

---

### **O - Open/Closed Principle**

**Definition:** Software entities should be open for extension but closed for modification. You should be able to add new functionality without changing existing code.

**Good Example from Fixify:**
```python
# Role-based middleware - extensible without modifying existing code
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

def require_service_provider(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "service_provider":
        raise HTTPException(status_code=403, detail="Service provider privileges required")
    return current_user

# Adding new role is EXTENSION without modifying existing dependencies
def require_moderator(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "moderator":
        raise HTTPException(status_code=403, detail="Moderator privileges required")
    return current_user
```

**Using Dependency Injection (OCP in Action):**
```python
@router.post("/orders")
def create_order(
    order_data: OrderCreateRequest,
    current_user: User = Depends(get_current_customer),  # Dependency injected
    db: Session = Depends(get_db)  # Dependency injected
):
    # Can change implementation without modifying this code
    order_service = OrderService(db)
    return order_service.create_order(current_user.id, order_data)
```

**Area for Improvement:**
```python
# ⚠️ Could be improved with Strategy Pattern
def get_order(self, order_id: int, user_id: int, user_role: str):
    order = self.order_repo.get_by_id(self.db, order_id)
    
    # Hardcoded role checks - not easily extensible
    if user_role == "customer" and order.customer_id != user_id:
        raise HTTPException(status_code=403)
    elif user_role == "service_provider":
        # Another hardcoded check
        pass
```

**Benefits:**
- New features without breaking existing code
- Reduced risk of regression bugs
- Cleaner, more stable codebase

---

### **L - Liskov Substitution Principle**

**Definition:** Objects of a superclass should be replaceable with objects of its subclasses without breaking the application.

**Good Example from Fixify:**
```python
# Repository classes maintain consistent contracts
class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

class OrderRepository:
    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()

# Both can be used interchangeably in similar contexts
# Services can work with any repository following this contract
```

**Response Schemas follow LSP:**
```python
class BaseResponse(BaseModel):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustomerResponse(BaseResponse):
    username: str
    email: str
    role: str

class OrderResponse(BaseResponse):
    order_number: str
    status: str
    total_amount: Decimal
```

**Benefits:**
- Predictable behavior when using subclasses
- Facilitates polymorphic code
- Prevents subtle bugs from violated contracts

---

### **I - Interface Segregation Principle**

**Definition:** Clients should not be forced to depend on interfaces they don't use. Create focused, specific interfaces.

**Good Example from Fixify:**
```python
# Focused, specific service interfaces
class AuthService:
    def login(self, request: LoginRequest) -> TokenResponse: pass
    def register_customer(self, request: CustomerRegisterRequest) -> User: pass

class OrderService:
    def create_order(self, customer_id: int, request: OrderCreateRequest): pass
    def get_customer_orders(self, customer_id: int) -> list: pass

# Each service has a specific, cohesive interface
# Clients only depend on methods they actually use
```

**Pydantic Schemas follow ISP:**
```python
# Minimal, focused request/response models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Not bloated with unused fields
```

**Area for Improvement:**
```python
# ⚠️ Current approach - always creates both repositories
class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository()  # Always created
        self.provider_repo = ProviderRepository()  # Always created, but not always used

# Better approach - Inject only needed dependencies
class AuthService:
    def __init__(self, db: Session, user_repo: UserRepository):
        self.user_repo = user_repo  # Only what's needed
```

**Benefits:**
- Smaller, more focused interfaces
- Reduced coupling between classes
- Easier to mock and test
- Clients use only what they need

---

### **D - Dependency Inversion Principle**

**Definition:** High-level modules should not depend on low-level modules. Both should depend on abstractions. Depend on abstractions, not concrete implementations.

**Excellent Example from Fixify:**
```python
# High-level: Router depends on abstraction (Depends)
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # Depends on abstraction, not concrete database instance
    auth_service = AuthService(db)
    return auth_service.login(payload)

# FastAPI Dependency Injection System
def get_current_user(
    token: str = Depends(oauth2_scheme),  # Depends on abstraction
    db: Session = Depends(get_db)  # Depends on abstraction
) -> User:
    """High-level function depends on abstractions, not implementations."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    user = db.query(User).filter(User.id == payload.get("id")).first()
    return user
```

**Role-Based Access Control via DIP:**
```python
# Abstraction layer for authorization
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403)
    return current_user

# Routes depend on abstraction, not authorization logic
@router.get("/admin/stats")
def get_stats(current: User = Depends(require_admin)):
    # Authorization logic is abstracted away
    return {...}
```

**Service Dependencies:**
```python
class OrderService:
    def __init__(self, db: Session):
        # Services depend on database abstraction (Session)
        self.db = db
        # Not tightly coupled to specific database implementation
        self.order_repo = OrderRepository()  # Could be swapped with another
        self.provider_repo = ProviderRepository()
```

**Benefits:**
- Low-level modules can be changed without affecting high-level code
- Easier testing (can mock dependencies)
- Flexible, pluggable architecture
- Reduced coupling

---

## Implementation in Fixify Backend

### **Architecture Overview**

```
┌─────────────────────────────────────────────┐
│         API Layer (Routers)                 │
│  - auth.py, customer.py, provider.py, etc.  │
└──────────────────┬──────────────────────────┘
                   │ (uses)
┌──────────────────▼──────────────────────────┐
│      Business Logic (Services)              │
│  - AuthService, OrderService, etc.          │
└──────────────────┬──────────────────────────┘
                   │ (uses)
┌──────────────────▼──────────────────────────┐
│    Data Access Layer (Repositories)         │
│  - UserRepository, OrderRepository, etc.    │
└──────────────────┬──────────────────────────┘
                   │ (uses)
┌──────────────────▼──────────────────────────┐
│   Database Models (SQLAlchemy ORM)          │
│  - User, Order, ServiceProvider, etc.       │
└─────────────────────────────────────────────┘
```

### **SOLID Compliance Summary**

| Principle | Score | Status | Notes |
|-----------|-------|--------|-------|
| **S**ingle Responsibility | 9/10 | ✅ Excellent | Clear separation: repositories, services, routers each have one job |
| **O**pen/Closed | 7/10 | ✅ Good | DI and middleware enable extension; some hardcoded role checks exist |
| **L**iskov Substitution | 8/10 | ✅ Good | Consistent repository/service interfaces; models follow contract |
| **I**nterface Segregation | 6/10 | ⚠️ Fair | Focused endpoints; could improve service constructors (ISP) |
| **D**ependency Inversion | 9/10 | ✅ Excellent | Strong use of FastAPI DI, repository pattern, abstraction layers |

---

## Best Practices

### **1. Use Type Hints**
```python
# ✅ GOOD: Clear contracts
def create_user(username: str, email: str, password: str) -> User:
    pass

# ❌ BAD: Ambiguous
def create_user(username, email, password):
    pass
```

### **2. Separation of Concerns**
```python
# ✅ GOOD: Each class has one reason to change
# Router - only handles HTTP
@router.post("/orders")
def create_order(order_data: OrderCreateRequest, db: Session = Depends(get_db)):
    service = OrderService(db)
    return service.create_order(order_data)

# Service - only handles business logic
class OrderService:
    def create_order(self, order_data: OrderCreateRequest) -> Order:
        # Validate, create order, return result
        pass

# Repository - only handles database
class OrderRepository:
    def create(self, db: Session, **kwargs) -> Order:
        # SQL operations only
        pass
```

### **3. Dependency Injection**
```python
# ✅ GOOD: Dependencies injected
@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return profile

# ❌ BAD: Hard dependencies
@router.get("/profile")
def get_profile():
    current_user = get_current_user()  # Hard to test/mock
    return profile
```

### **4. Composition Over Inheritance**
```python
# ✅ GOOD: Composition
class OrderService:
    def __init__(self, db: Session):
        self.order_repo = OrderRepository()
        self.provider_repo = ProviderRepository()

# ❌ BAD: Deep inheritance hierarchies
class AdminOrderService(OrderService):
    pass
```

### **5. Use Abstractions (Protocols/Interfaces)**
```python
# ✅ GOOD: Python 3.8+
from typing import Protocol

class RepositoryProtocol(Protocol):
    def get_by_id(self, id: int): ...
    def create(self, **kwargs): ...

# ❌ OLD: No clear interface
class Repository:
    pass
```

---

## Common Anti-Patterns to Avoid

### **God Object**
```python
# ❌ BAD: One class doing everything
class User:
    def save_to_database(self): pass
    def send_email(self): pass
    def generate_report(self): pass
    def validate_payment(self): pass
```

### **Tight Coupling**
```python
# ❌ BAD: Direct instantiation
class OrderService:
    def __init__(self):
        self.db = Database()  # Tightly coupled
        self.email = EmailService()  # Tightly coupled
```

### **Leaky Abstraction**
```python
# ❌ BAD: Implementation details leak
class OrderService:
    def create_order(self) -> Order:
        # Caller knows about database, SQL queries
        query = "INSERT INTO orders..."
        return execute_query(query)
```

### **Feature Envy**
```python
# ❌ BAD: Excessive use of another object's data
class OrderService:
    def get_provider_rating(self, order):
        # Too much knowledge of Order's internal structure
        return calculate_rating(order.provider.reviews.all())
```

---

## Conclusion

The Fixify Backend demonstrates strong adherence to SOLID principles and OOP concepts through:

1. **Clear separation** of repositories, services, and routers
2. **Dependency injection** via FastAPI's elegant DI system
3. **Abstraction layers** that hide implementation complexity
4. **Consistent interfaces** across similar classes
5. **Role-based access control** enabling extensibility

### Key Takeaways:
- ✅ SOLID principles make code more maintainable
- ✅ OOP concepts provide structure and organization
- ✅ Proper architecture scales better
- ✅ Good design reduces bugs and enables testing
- ✅ Continuous improvement: review and refactor regularly

### Next Steps for Improvement:
1. Add protocol/interface definitions for repositories
2. Use Strategy pattern for role-based authorization
3. Implement factory pattern for service creation
4. Add abstract base classes for common functionality
5. Create comprehensive unit tests for each layer

---

## References

- **SOLID Principles:** https://en.wikipedia.org/wiki/SOLID
- **Design Patterns:** https://refactoring.guru/design-patterns
- **Python Best Practices:** https://pep8.org/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
