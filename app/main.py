import logging
import os
import time

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import OperationalError
from app.db.models import Base
from app.db.database import SessionLocal, engine
from app.db.models import User
from app.utils.hashing import hash_password
from app.routers import (
    auth, admin, customer, provider, order, review, contact, message
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fixify API",
    version="1.0.0",
    description="Backend API for Fixify - Service provider marketplace"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fixify-a-servicemarketplace.netlify.app",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_ADMIN_USERNAME = "admin@fixify"
DEFAULT_ADMIN_EMAIL = "admin@fixify"
DEFAULT_ADMIN_PASSWORD = "rehman@16@"

def _initialize_database_with_retry() -> None:
    """Create tables with retry to tolerate transient cloud DB startup failures."""
    max_retries = int(os.getenv("DB_INIT_MAX_RETRIES", "5"))
    delay_seconds = float(os.getenv("DB_INIT_RETRY_DELAY", "2"))
    require_db_on_startup = os.getenv("DB_INIT_REQUIRED", "false").lower() == "true"

    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database initialization completed")
            return
        except OperationalError as exc:
            if attempt == max_retries:
                if require_db_on_startup:
                    raise
                logger.error(
                    "Database init failed after %s attempts; continuing startup because DB_INIT_REQUIRED is false: %s",
                    max_retries,
                    exc,
                )
                return
            logger.warning(
                "Database init failed (attempt %s/%s): %s. Retrying in %.1fs",
                attempt,
                max_retries,
                exc,
                delay_seconds,
            )
            time.sleep(delay_seconds)


def _seed_default_admin() -> None:
    """Create or refresh the default admin account."""
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(
            (User.username == DEFAULT_ADMIN_USERNAME) | (User.email == DEFAULT_ADMIN_EMAIL)
        ).first()

        password_hash = hash_password(DEFAULT_ADMIN_PASSWORD)

        if admin_user:
            admin_user.username = DEFAULT_ADMIN_USERNAME
            admin_user.email = DEFAULT_ADMIN_EMAIL
            admin_user.password_hash = password_hash
            admin_user.role = "admin"
            admin_user.token_version = 0
            logger.info("Default admin account refreshed: %s", DEFAULT_ADMIN_USERNAME)
        else:
            db.add(User(
                username=DEFAULT_ADMIN_USERNAME,
                email=DEFAULT_ADMIN_EMAIL,
                password_hash=password_hash,
                role="admin",
                token_version=0,
            ))
            logger.info("Default admin account created: %s", DEFAULT_ADMIN_USERNAME)

        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to seed default admin account")
        raise
    finally:
        db.close()


@app.on_event("startup")
def startup_event() -> None:
    _initialize_database_with_retry()
    _seed_default_admin()

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(customer.router)
app.include_router(provider.router)
app.include_router(order.router)
app.include_router(review.router)
app.include_router(contact.router)
app.include_router(message.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Fixify API",
        "version": "1.0.0",
        "docs": "/docs"
    }
