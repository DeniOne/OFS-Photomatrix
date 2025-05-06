from fastapi import APIRouter
import logging

# Явно импортируем роутеры из модулей, минуя __init__.py
from app.api.endpoints.auth import router as login_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.organizations import router as organizations_router
from app.api.endpoints.divisions import router as divisions_router
from app.api.endpoints.positions import router as positions_router
from app.api.endpoints.staff import router as staff_router
from app.api.endpoints.value_products import router as value_products_router
from app.api.endpoints.functions import router as functions_router
from app.api.endpoints.sections import router as sections_router
from app.api.endpoints.orgchart import router as orgchart_router

logger = logging.getLogger(__name__)

# Создаем и настраиваем основной роутер API
api_router = APIRouter()
api_router.include_router(login_router, prefix="", tags=["login"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(organizations_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(divisions_router, prefix="/divisions", tags=["divisions"])
api_router.include_router(positions_router, prefix="/positions", tags=["positions"])
api_router.include_router(staff_router, prefix="/staff", tags=["staff"])
api_router.include_router(value_products_router, prefix="/value_products", tags=["value_products"])
api_router.include_router(functions_router, prefix="/functions", tags=["functions"])
api_router.include_router(sections_router, prefix="/sections", tags=["sections"])
api_router.include_router(orgchart_router, prefix="/orgchart", tags=["orgchart"])

logger.info("API роутеры настроены")
