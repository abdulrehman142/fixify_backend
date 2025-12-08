from datetime import datetime, timedelta
from jose import jwt
from typing import Dict
from core.config import settings

def create_access_token(data: Dict[str, object]) -> str:
    """
    Create a JWT access token containing the provided payload and an expiry.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    to_encode["token_version"] = data["token_version"]
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token
