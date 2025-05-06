from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.base import get_db
from app.crud import user as crud_user
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.token import Token, InvitationCodeSchema

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

@router.post("/activate-code", response_model=dict)
async def activate_invitation_code(
    *,
    db: AsyncSession = Depends(get_db),
    data: dict,
) -> Any:
    """
    Проверить и активировать код приглашения
    """
    logger.info(f"Попытка активации кода: {data}")
    
    code = data.get("code")
    telegram_id = data.get("telegram_id")
    
    if not code or not telegram_id:
        logger.warning(f"Отсутствуют обязательные параметры: код={code}, telegram_id={telegram_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать код и telegram_id",
        )
    
    # Проверяем код приглашения
    user = await crud_user.get_by_activation_code(db, activation_code=code)
    
    if not user:
        logger.warning(f"Код активации не найден: {code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Код активации не найден",
        )
    
    # Проверяем, не использован ли уже код
    if user.is_active:
        logger.warning(f"Код активации уже использован: {code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код активации уже использован",
        )
    
    # Активируем пользователя и сохраняем telegram_id
    user_update = {"is_active": True, "telegram_id": telegram_id}
    updated_user = await crud_user.update(db, db_obj=user, obj_in=user_update)
    
    logger.info(f"Успешная активация кода для пользователя: {updated_user.email}")
    
    return {
        "success": True,
        "user_id": updated_user.id,
        "email": updated_user.email,
    }