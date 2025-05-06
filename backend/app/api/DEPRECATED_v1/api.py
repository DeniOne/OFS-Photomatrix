from fastapi import APIRouter, Request
import logging

from app.api.v1.endpoints import (
    login, 
    utils, 
    organization,
    division,
    section,
    position,
    staff,
    function,
    users, # Добавили импорт роутера users
    orgchart # Импортируем новый endpoint для оргчарта
)

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Глобальный обработчик OPTIONS запросов для CORS preflight
@api_router.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """Обработчик OPTIONS-запросов для CORS preflight"""
    logger.info(f"OPTIONS запрос к пути: {full_path}")
    return {}

api_router.include_router(login.router, tags=["login"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(organization.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(division.router, prefix="/divisions", tags=["divisions"])
api_router.include_router(section.router, prefix="/sections", tags=["sections"])
api_router.include_router(position.router, prefix="/positions", tags=["positions"])
api_router.include_router(staff.router, prefix="/staff", tags=["staff"])
api_router.include_router(function.router, prefix="/functions", tags=["functions"])
# Добавляем роутер users
api_router.include_router(users.router, prefix="/users", tags=["users"]) 
# Добавляем роутер для организационной диаграммы
api_router.include_router(orgchart.router, prefix="/orgchart", tags=["orgchart"]) 