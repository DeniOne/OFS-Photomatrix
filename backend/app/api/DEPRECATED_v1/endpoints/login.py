from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.utils import verify_activation_code

router = APIRouter()

@router.post("/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, получение токена для доступа к API
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/activate", response_model=schemas.ActivationResponse)
async def activate_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    activation_data: schemas.UserActivation
) -> Any:
    """
    Активация пользователя по коду активации
    """
    activation_code = activation_data.activation_code
    
    # Проверяем правильность кода и получаем пользователя
    user = await verify_activation_code(db, activation_code)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid activation code")
    
    # Хешируем пароль
    hashed_password = get_password_hash(activation_data.password)
    
    # Обновляем пользователя: устанавливаем пароль, активируем аккаунт, сбрасываем код активации
    user_update = {"password": hashed_password, "is_active": True, "activation_code": None}
    user = await crud.user.update(db, db_obj=user, obj_in=user_update)
    
    # Создаем токен аутентификации
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(user.id, expires_delta=access_token_expires)
    
    return {
        "message": "User successfully activated",
        "is_active": True,
        "access_token": access_token,
        "token_type": "bearer",
    } 