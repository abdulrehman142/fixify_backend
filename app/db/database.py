import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# Use pymysql driver if mysql:// is specified
if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Project root for locating certificate files
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

connect_args = {
    "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "30")),
    "read_timeout": int(os.getenv("DB_READ_TIMEOUT", "30")),
    "write_timeout": int(os.getenv("DB_WRITE_TIMEOUT", "30")),
}

# Configure SSL for cloud-hosted MySQL databases
ca_pem_path = os.path.join(PROJECT_ROOT, "ca.pem")
if os.path.exists(ca_pem_path):
    connect_args["ssl"] = {
        "ca": ca_pem_path
    }

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
