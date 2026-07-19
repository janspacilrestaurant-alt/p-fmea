from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Role, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

_ROLE_RANK = {Role.viewer: 0, Role.engineer: 1, Role.admin: 2}


def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)


def create_access_token(subject: str, org_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "org": org_id, "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    exc = HTTPException(status.HTTP_401_UNAUTHORIZED, "Neplatné přihlašovací údaje",
                        {"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
    except JWTError:
        raise exc
    if not user_id:
        raise exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise exc
    return user


def require_role(minimum: Role):
    def _dep(user: Annotated[User, Depends(get_current_user)]) -> User:
        if _ROLE_RANK[user.role] < _ROLE_RANK[minimum]:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Nedostatečná oprávnění")
        return user
    return _dep
