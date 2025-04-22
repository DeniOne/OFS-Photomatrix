from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.base import get_db
from app.crud import user as crud_user
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.token import Token

# Получаем логгер
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Получить JWT токен доступа
    """
    # Добавляем логирование для отладки
    logger.info(f"Попытка входа пользователя: {form_data.username}")
    
    user = await crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    
    if not user:
        logger.warning(f"Неудачная попытка входа для пользователя: {form_data.username} - неверные учетные данные")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not await crud_user.is_active(user):
        logger.warning(f"Попытка входа для неактивного пользователя: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь"
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(user.id, expires_delta=access_token_expires)
    
    logger.info(f"Успешный вход пользователя: {form_data.username}")
    
    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.post("/test-token", response_model=dict)
async def test_token() -> Any:
    """
    Тестовый эндпоинт для проверки токена
    """
    return {"msg": "Токен работает"} 