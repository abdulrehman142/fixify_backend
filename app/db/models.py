from sqlalchemy import Column, BigInteger, String, Enum, TIMESTAMP, text, Integer, ForeignKey, Numeric, Text, Date, Time
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(128), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin","service_provider","customer", name="user_roles"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    token_version = Column(Integer, default=0, nullable=False)
    
    # Relationships
    service_provider = relationship("ServiceProvider", back_populates="user", uselist=False)
    customer_orders = relationship("Order", foreign_keys="Order.customer_id", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")


class ServiceProvider(Base):
    __tablename__ = "service_providers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, unique=True)
    service_category = Column(Enum(
        "cleaner", "electrician", "plumber", "mechanic", 
        "mover", "technician", "painter", "gardener", "carpenter",
        name="service_categories"
    ), nullable=False)
    approval_status = Column(Enum("pending", "approved", "rejected", name="approval_status"), 
                            nullable=False, default="pending")
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    phone = Column(String(20), nullable=False)
    business_name = Column(String(255), nullable=True)
    experience_years = Column(Integer, nullable=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    bio = Column(Text, nullable=True)
    city = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), 
                       onupdate=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    user = relationship("User", back_populates="service_provider")
    orders = relationship("Order", back_populates="service_provider")
    reviews = relationship("Review", back_populates="service_provider")


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_number = Column(String(50), nullable=False, unique=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    service_provider_id = Column(BigInteger, ForeignKey("service_providers.id"), nullable=True)
    service_name = Column(String(255), nullable=False)
    service_category = Column(Enum(
        "cleaner", "electrician", "plumber", "mechanic", 
        "mover", "technician", "painter", "gardener", "carpenter",
        name="service_categories"
    ), nullable=False)
    service_date = Column(Date, nullable=False)
    service_time = Column(Time, nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    special_instructions = Column(Text, nullable=True)
    status = Column(Enum("pending", "assigned", "in_progress", "completed", name="order_status"), 
                   nullable=False, default="pending")
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), 
                       onupdate=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], back_populates="customer_orders")
    service_provider = relationship("ServiceProvider", back_populates="orders")
    review = relationship("Review", back_populates="order", uselist=False)
    messages = relationship("Message", back_populates="order")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, unique=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    service_provider_id = Column(BigInteger, ForeignKey("service_providers.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    order = relationship("Order", back_populates="review")
    customer = relationship("User", back_populates="reviews")
    service_provider = relationship("ServiceProvider", back_populates="reviews")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    sender_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    sender_type = Column(Enum("customer", "service_provider", name="sender_types"), nullable=False)
    message_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    order = relationship("Order", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
