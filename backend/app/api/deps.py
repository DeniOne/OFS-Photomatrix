from typing import Generator, Optional, Union

from fastapi import Depends, HTTPException, status, Header, Request
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

# API ключ для телеграм-бота
# В реальном сценарии это должно быть в .env или в базе данных
API_KEY = "test_api_key_1234567890"

# OAuth2 с Bearer Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key: Optional[str] = Header(None, alias="Api-Key"),
    authorization: Optional[str] = Header(None),
) -> Optional[str]:
    """
    Проверить наличие API-ключа в различных заголовках
    """
    # Проверяем X-API-Key
    if x_api_key:
        auth_logger.debug(f"Получен X-API-Key: {x_api_key[:5]}...")
        if x_api_key == API_KEY:
            auth_logger.debug("X-API-Key верифицирован")
            return x_api_key
    
    # Проверяем Api-Key
    if api_key:
        auth_logger.debug(f"Получен Api-Key: {api_key[:5]}...")
        if api_key == API_KEY:
            auth_logger.debug("Api-Key верифицирован")
            return api_key
            
    # Проверяем Bearer токен на случай, если в нем API ключ
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        auth_logger.debug(f"Получен Bearer токен (возможно API ключ): {token[:5]}...")
        if token == API_KEY:
            auth_logger.debug("Bearer API-Key верифицирован")
            return token
    
    return None

async def get_current_user_or_api_key(
    db: AsyncSession = Depends(get_db), 
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(get_api_key),
) -> Union[User, str]:
    """
    Получить текущего пользователя по JWT токену или проверить API ключ
    """
    # ВРЕМЕННЫЙ ОБХОДНОЙ ПУТЬ: всегда возвращать суперпользователя для демо
    # TODO: УДАЛИТЬ В ПРОДАКШЕНЕ!!! СЕРЬЕЗНАЯ ДЫРА БЕЗОПАСНОСТИ!!!
    auth_logger.warning("⚠️ DEVELOPMENT MODE: Bypassing authentication!")
    
    # Находим первого суперпользователя в базе
    user = await crud_user.get_superuser(db)
    if user:
        auth_logger.debug(f"DEV MODE: Автологин как {user.email}")
        return user
        
    # Если API ключ есть и он правильный, пропускаем и возвращаем маркер
    if api_key:
        auth_logger.debug("Доступ разрешен через API ключ")
        return "api_key_authenticated"
        
    # Если API ключа нет, проверяем JWT
    if not token:
        auth_logger.error("Отсутствует токен и API-ключ")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима аутентификация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        auth_logger.debug(f"Начало верификации JWT токена: {token[:10]}...")
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

async def get_current_active_user_or_api_key(
    current_user_or_api_key: Union[User, str] = Depends(get_current_user_or_api_key)
) -> Union[User, str]:
    """
    Получить текущего активного пользователя или пройти по API ключу
    """
    # Если аутентификация по API ключу, пропускаем
    if isinstance(current_user_or_api_key, str) and current_user_or_api_key == "api_key_authenticated":
        return current_user_or_api_key
    
    # Иначе проверяем активность пользователя
    if not await crud_user.is_active(current_user_or_api_key):
        auth_logger.warning(f"Попытка доступа неактивного пользователя: {current_user_or_api_key.email} (ID: {current_user_or_api_key.id})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь"
        )
    
    auth_logger.debug(f"Активный пользователь подтвержден: {current_user_or_api_key.email} (ID: {current_user_or_api_key.id})")
    return current_user_or_api_key

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

async def get_current_active_superuser(current_user: User = Depends(get_current_superuser)) -> User:
    """Получить текущего активного суперпользователя.
    Этот алиас добавлен для совместимости со старым кодом, который ожидает функцию
    `get_current_active_superuser`. Она проверяет, что суперпользователь также активен.
    """
    if not await crud_user.is_active(current_user):
        auth_logger.warning(
            f"Попытка доступа неактивного суперпользователя: {current_user.email} (ID: {current_user.id})"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь"
        )
    return current_user

# ------------------------------------------------------------
# Совместимость: старые endpoint'ы вызывают get_async_db, добавим алиас
# ------------------------------------------------------------
async def get_async_db() -> AsyncSession:
    """Alias to get_db for endpoints expecting get_async_db."""
    async for session in get_db():
        yield session 