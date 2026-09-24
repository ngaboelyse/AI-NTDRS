from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt

from app.core.config import settings

JWT_ALGORITHM = "HS256"


def create_access_token(subject: str, expires_delta_minutes: int | None = None) -> str:
    expire_minutes = expires_delta_minutes or settings.access_token_expire_minutes
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {
        "sub": subject,
        "exp": expire_time,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)
