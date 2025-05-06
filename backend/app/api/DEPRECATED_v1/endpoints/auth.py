from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from typing import Any

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.logging import auth_logger

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> schemas.Token:
    """OAuth2 совместимый эндпоинт для получения токена доступа"""
    auth_logger.info(f"Попытка входа пользователя: {form_data.username}")
    
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    
    if not user:
        auth_logger.warning(f"Неудачная попытка входа: {form_data.username} - неверные учетные данные")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        auth_logger.warning(f"Попытка входа неактивного пользователя: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    
    auth_logger.info(f"Успешный вход пользователя: {form_data.username} (ID: {user.id})")
    
    return schemas.Token(
        access_token=token,
        token_type="bearer",
    )

@router.post("/activate", response_model=schemas.Msg)
async def activate_user(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    activation_data: schemas.UserActivate
) -> schemas.Msg:
    """Активация пользователя с помощью кода и установка пароля."""
    auth_logger.info(f"Попытка активации пользователя с кодом: {activation_data.activation_code[:3]}...")
    
    user = await crud.user.get_by_activation_code(db, code=activation_data.activation_code)
    if not user:
        auth_logger.warning(f"Неверный код активации: {activation_data.activation_code[:3]}...")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Invalid activation code."
        )
    if user.hashed_password is not None:
         auth_logger.warning(f"Попытка повторной активации пользователя: {user.email} (ID: {user.id})")
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User is already activated."
        )
        
    await crud.user.activate_user(db, user=user, password=activation_data.password)
    auth_logger.info(f"Пользователь успешно активирован: {user.email} (ID: {user.id})")
    return schemas.Msg(msg="User activated successfully")

@router.post("/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """Тестовый эндпоинт для проверки токена"""
    auth_logger.debug(f"Проверка токена для пользователя: {current_user.email} (ID: {current_user.id})")
    return current_user 