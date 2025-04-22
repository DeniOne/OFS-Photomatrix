from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User
from app.crud import user as crud_user
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas.token import TokenPayload
from app.core.logging import auth_logger

# OAuth2 с Bearer Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Получить текущего пользователя по JWT токену
    """
    try:
        auth_logger.debug(f"Начало верификации токена: {token[:10]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        auth_logger.debug(f"Токен успешно декодирован, sub: {token_data.sub}")
    except (JWTError, ValidationError) as e:
        auth_logger.error(f"Ошибка при декодировании токена: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = await crud_user.get(db, id=token_data.sub)
    
    if not user:
        auth_logger.error(f"Пользователь с ID {token_data.sub} не найден")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    auth_logger.debug(f"Пользователь {user.email} (ID: {user.id}) успешно аутентифицирован")
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Получить текущего активного пользователя
    """
    if not await crud_user.is_active(current_user):
        auth_logger.warning(f"Попытка доступа неактивного пользователя: {current_user.email} (ID: {current_user.id})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь"
        )
    
    auth_logger.debug(f"Активный пользователь подтвержден: {current_user.email} (ID: {current_user.id})")
    return current_user

async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    Получить текущего суперпользователя
    """
    if not await crud_user.is_superuser(current_user):
        auth_logger.warning(f"Попытка доступа без прав суперпользователя: {current_user.email} (ID: {current_user.id})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    auth_logger.debug(f"Суперпользователь подтвержден: {current_user.email} (ID: {current_user.id})")
    return current_user 