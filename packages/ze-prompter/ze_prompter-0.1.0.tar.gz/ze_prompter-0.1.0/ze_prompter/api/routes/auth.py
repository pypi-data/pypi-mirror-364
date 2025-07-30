from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ...models import get_db
from ...core.auth import AuthManager, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    auth_manager = AuthManager(db)
    user = auth_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_manager.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
async def register_user(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    auth_manager = AuthManager(db)

    # Check if user already exists
    if auth_manager.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    user = auth_manager.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )