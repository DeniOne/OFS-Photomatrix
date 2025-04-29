import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app import crud, models

logger = logging.getLogger(__name__)

async def verify_activation_code(db: AsyncSession, activation_code: str) -> Optional[models.User]:
    """
    Проверяет валидность кода активации и возвращает связанного пользователя
    """
    if not activation_code:
        logger.warning("Attempt to verify empty activation code")
        return None
    
    user = await crud.user.get_by_activation_code(db, activation_code=activation_code)
    
    if not user:
        logger.warning(f"Invalid activation code used: {activation_code}")
        return None
    
    if user.is_active:
        logger.warning(f"Activation code used for already active user: {user.id}")
        return None
    
    logger.info(f"Valid activation code for user: {user.id}")
    return user 