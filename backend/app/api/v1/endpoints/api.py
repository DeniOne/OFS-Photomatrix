from fastapi import APIRouter, Request
import logging

from .auth import router as auth_router
from .user import router as user_router
from .utils import router as utils_router
from .section import router as section_router
from .organization import router as organization_router
from .position import router as position_router
from .division import router as division_router
from .staff import router as staff_router
from .function import router as function_router
from .telegram_bot import router as telegram_bot_router

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Предфлайт CORS для всех эндпоинтов
@api_router.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """
    Глобальный обработчик OPTIONS-запросов для всех эндпоинтов API v1
    """
    logger.info(f"OPTIONS запрос к пути: {full_path}")
    return {}

# Регистрация роутеров API v1
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(utils_router, prefix="/utils", tags=["utils"])
api_router.include_router(section_router, prefix="/section", tags=["section"])
api_router.include_router(organization_router, prefix="/organization", tags=["organization"])
api_router.include_router(position_router, prefix="/position", tags=["position"])
api_router.include_router(division_router, prefix="/division", tags=["division"])
api_router.include_router(staff_router, prefix="/staff", tags=["staff"])
api_router.include_router(function_router, prefix="/function", tags=["function"])
api_router.include_router(telegram_bot_router, prefix="/telegram-bot", tags=["telegram-bot"]) 