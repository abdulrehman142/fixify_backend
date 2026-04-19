import os
import certifi
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# Use pymysql driver if mysql:// is specified
if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

connect_args = {
    "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "30")),
    "read_timeout": int(os.getenv("DB_READ_TIMEOUT", "30")),
    "write_timeout": int(os.getenv("DB_WRITE_TIMEOUT", "30")),
}

if DATABASE_URL and DATABASE_URL.startswith("mysql+pymysql://"):
    try:
        db_host = (make_url(DATABASE_URL).host or "").lower()
    except Exception:
        db_host = ""

    # Enable TLS for Aiven-hosted databases (required for production security).
    if db_host.endswith("aivencloud.com"):
        ssl_config = {"ssl_verify_cert": False, "ssl_verify_identity": False}
        
        # Try to find a valid CA certificate file
        ca_candidates = [
            os.getenv("MYSQL_SSL_CA", ""),
            certifi.where(),
            "/etc/ssl/certs/ca-certificates.crt",
            "/etc/ssl/cert.pem",
            "/etc/pki/tls/certs/ca-bundle.crt",
        ]
        ca_path = next((path for path in ca_candidates if path and os.path.exists(path)), None)
        
        if ca_path:
            ssl_config["ca"] = os.path.abspath(ca_path)
        
        connect_args["ssl"] = ssl_config

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
