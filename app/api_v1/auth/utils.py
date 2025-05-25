import jwt
from fastapi import HTTPException
from app.core.config import settings
import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import timedelta, datetime, timezone
import uuid
import logging
from app.api_v1.utils.setup_logging import setup_logging
logger = setup_logging(__name__)

serializer = URLSafeTimedSerializer(
    secret_key=settings.oauth2.AUTH_SECRET, salt="email-configuration"
)


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_timedelta: timedelta | None = None,
    expire_minute: int = settings.auth_jwt.access_token_expire_minutes,
):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minute)
    to_encode.update(exp=expire, iat=now, jti=str(uuid.uuid4()))

    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)

    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)


def create_url_safe_mail_token(data: dict):
    mail_token = serializer.dumps(data, salt="email-configuration")
    return mail_token


def decode_url_safe_mail_token(token: str, max_age_seconds: int = 3600) -> dict:
    try:
        data = serializer.loads(token, max_age=max_age_seconds)
        return data
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Token has expired")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid token")
