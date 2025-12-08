# Fixify API - Service Provider Marketplace Backend

## 📋 Overview

Fixify is a backend API for a service provider marketplace platform that connects customers with qualified service providers across various categories. The system handles user management, authentication, service orders, reviews, and messaging between customers and providers.

## 🛠️ Technologies Used

### Core Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI web server for running the FastAPI application

### Database
- **SQLAlchemy** - SQL toolkit and Object-Relational Mapping (ORM)
- **MySQL** - Relational database with PyMySQL driver
- **Alembic** - Database migrations (available for schema management)

### Authentication & Security
- **Python-Jose** - JWT token implementation for authentication
- **Passlib with Bcrypt** - Password hashing and verification
- **Pydantic** - Data validation and settings management

### Additional Libraries
- **python-dotenv** - Environment variable management
- **FastAPI CORS Middleware** - Cross-Origin Resource Sharing support

## 📦 Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── create_admin.py         # Admin user creation script
├── requirements.txt        # Python dependencies
├── core/
│   ├── config.py          # Configuration and settings
│   ├── dependencies.py    # FastAPI dependencies
│   └── security.py        # Authentication and authorization logic
├── db/
│   ├── database.py        # Database connection and session management
│   ├── models.py          # SQLAlchemy ORM models
│   └── schemas.py         # Pydantic request/response schemas
├── migrations/
│   └── *.sql              # Database migration scripts
├── repositories/          # Data access layer
│   ├── user_repository.py
│   ├── contact_repository.py
│   ├── message_repository.py
│   ├── order_repository.py
│   ├── provider_repository.py
│   └── review_repository.py
├── routers/               # API route handlers
│   ├── admin.py
│   ├── auth.py
│   ├── contact.py
│   ├── customer.py
│   ├── message.py
│   ├── order.py
│   ├── provider.py
│   └── review.py
├── services/              # Business logic layer
│   ├── auth_service.py
│   ├── contact_service.py
│   ├── customer_service.py
│   ├── message_service.py
│   ├── order_service.py
│   ├── provider_service.py
│   └── review_service.py
└── utils/                 # Utility functions
    ├── hashing.py         # Password hashing utilities
    ├── order_number.py    # Order number generation
    ├── service_mapper.py  # Service category mapping
    └── validators.py      # Data validation helpers
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** 
- **MySQL Server** (running locally or remotely)
- **pip** (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Backend
   ```

2. **Install Python dependencies:**
   ```bash
   cd app
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Create a `.env` file in the `app` directory
   - Set the following variables:
   ```env
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/SdaProjectDb
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```
   - Replace `username` and `password` with your MySQL credentials
   - Create the database `SdaProjectDb` in MySQL if it doesn't exist

4. **Create an admin user:**
   ```bash
   python create_admin.py
   ```
   Follow the prompts to enter admin username and email. The password will be prompted and securely hashed.

### Running the Application

**Start the development server:**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

**Access the API documentation:**
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Production Deployment

For production deployment:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Update the CORS settings in `main.py` to allow only your frontend domain:
```python
allow_origins=["https://yourdomain.com"]
```

## 📚 API Features

### Authentication Endpoints (`/auth`)
- User registration
- User login
- Token refresh
- Password management

### Admin Endpoints (`/admin`)
- User management
- System administration
- Analytics and monitoring

### Customer Endpoints (`/customer`)
- Browse services
- Place orders
- Track order status
- View service provider profiles

### Provider Endpoints (`/provider`)
- Manage service profiles
- View received orders
- Update service availability
- Track service history

### Order Endpoints (`/order`)
- Create and manage orders
- Update order status
- Track order progress

### Review Endpoints (`/review`)
- Submit reviews for completed services
- View provider ratings

### Contact Endpoints (`/contact`)
- Submit contact/support requests
- Manage contact information

### Message Endpoints (`/message`)
- Send messages between customers and providers
- Message history

## 🗂️ Service Categories

The platform supports the following service categories:
- Cleaner
- Electrician
- Plumber
- Mechanic
- Mover
- Technician
- Painter
- Gardener
- Carpenter

## 🔐 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - Bcrypt hashing for secure password storage
- **Role-Based Access Control** - Three roles: admin, service_provider, customer
- **CORS Protection** - Configurable cross-origin resource sharing
- **Token Versioning** - Support for token invalidation

## 📝 Database Schema

Key tables:
- **users** - User accounts with roles (admin, service_provider, customer)
- **service_providers** - Service provider profiles
- **orders** - Service orders
- **reviews** - Service reviews and ratings
- **messages** - Direct messaging between users
- **contacts** - Contact/support requests

## 🛠️ Development

### Running Tests
```bash
pytest
```

### Code Structure Patterns
- **Repository Pattern** - Data access abstraction
- **Service Layer** - Business logic separation
- **Router Pattern** - Clean API endpoint organization
- **Dependency Injection** - FastAPI dependency system

## 🐛 Troubleshooting

### Database Connection Issues
- Verify MySQL server is running
- Check DATABASE_URL in `.env` file
- Ensure the database `SdaProjectDb` exists

### Admin Creation Issues
- Ensure no admin with the same username/email exists
- Run `python create_admin.py` from the `app` directory

### CORS Errors
- Update `allow_origins` in `main.py` with your frontend URL
- During development, `"*"` allows all origins

## 📄 License

This project is part of the SdaProject initiative.

## 👥 Contributors

- Backend Team - SageCore

---

For more information or issues, please refer to the project repository.
# fixify_backend
# fixify_backend
# fixify_backend
