import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get DATABASE_URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:tomojelly@localhost:3306/SdaProjectDb")

# Use pymysql driver if mysql:// is specified
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
