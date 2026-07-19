from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (create_access_token, get_current_user,
                               hash_password, require_role, verify_password)
from app.db import get_db
from app.models import Role, User
from app.schemas import Token, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()],
          db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.email == form.username))
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Nesprávný e-mail nebo heslo")
    token = create_access_token(str(user.id), str(user.organization_id), user.role.value)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: Annotated[User, Depends(get_current_user)]):
    return user


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate,
                admin: Annotated[User, Depends(require_role(Role.admin))],
                db: Annotated[Session, Depends(get_db)]):
    if db.scalar(select(User).where(User.email == payload.email,
                                    User.organization_id == admin.organization_id)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Uživatel s tímto e-mailem již existuje")
    user = User(organization_id=admin.organization_id, email=payload.email,
                full_name=payload.full_name, role=payload.role,
                hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
