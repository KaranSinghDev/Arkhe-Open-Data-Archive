from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User

_ALGORITHM = "HS256"
_TOKEN_EXPIRE_DAYS = 30


def create_jwt(user_id: str, orcid_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "orcid": orcid_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def verify_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
        if payload.get("sub") is None:
            raise ValueError("Invalid token")
        return payload
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc


async def get_or_create_user(
    db: AsyncSession,
    orcid_id: str,
    name: str,
    email: str | None = None,
) -> User:
    result = await db.execute(select(User).where(User.orcid_id == orcid_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=uuid4(),
            orcid_id=orcid_id,
            name=name,
            email=email,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif user.name != name or (email and user.email != email):
        user.name = name
        if email:
            user.email = email
        await db.commit()
        await db.refresh(user)

    return user
