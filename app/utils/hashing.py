from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    # Pre-hash with SHA256 to handle passwords > 72 bytes
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(password_hash)

def verify_password(password: str, hashed: str) -> bool:
    # Pre-hash with SHA256 to match the stored hash
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.verify(password_hash, hashed)
