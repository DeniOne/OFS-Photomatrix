from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict

from app import crud, models, schemas
from app.api import deps
from app.core import security

router = APIRouter()

class HealthCheck(BaseModel):
    status: str = "OK"
    version: str = "1.0.0"

@router.get("/health-check", response_model=HealthCheck)
async def health_check() -> Any:
    """
    Проверка работоспособности API
    """
    return HealthCheck()

@router.post("/validate-invitation-code", response_model=Dict[str, Any])
async def validate_invitation_code(
    *,
    db: AsyncSession = Depends(deps.get_db),
    code: str,
    telegram_id: int
) -> Dict[str, Any]:
    """
    Проверка валидности кода приглашения для Telegram-бота
    """
    # Здесь должна быть логика проверки кода приглашения
    # Для примера, будем считать, что любой код длиной 8 символов валиден
    if len(code) == 8:
        return {
            "valid": True,
            "position_id": 1,
            "position_name": "Разработчик",
            "division_id": 1,
            "division_name": "IT отдел"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid invitation code")
        
@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получение информации о текущем пользователе
    """
    return current_user 