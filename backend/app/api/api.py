import logging

from fastapi import APIRouter

from app.api.endpoints import (
    auth,
    users,
    organizations,
    divisions,
    sections,
    positions,
    value_products,
    functions,
    staff,
    orgchart
)

api_router = APIRouter()

# Логируем перед подключением каждого роутера (для отладки 405)
logging.info("Подключение роутера /auth...")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
logging.info("Подключение роутера /users...")
api_router.include_router(users.router, prefix="/users", tags=["users"])
logging.info("Подключение роутера /organizations...")
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
logging.info("Подключение роутера /divisions...")
api_router.include_router(divisions.router, prefix="/divisions", tags=["divisions"])
logging.info("Подключение роутера /sections...")
api_router.include_router(sections.router, prefix="/sections", tags=["sections"])
logging.info("Подключение роутера /positions...")
api_router.include_router(positions.router, prefix="/positions", tags=["positions"])
logging.info("Подключение роутера /value-products...")
api_router.include_router(value_products.router, prefix="/value-products", tags=["value-products"])
logging.info("Подключение роутера /functions...")
api_router.include_router(functions.router, prefix="/functions", tags=["functions"])
logging.info("Подключение роутера /staff...")
api_router.include_router(staff.router, prefix="/staff", tags=["staff"])

# --- Подключаем роутер оргструктуры ---
logging.info("Подключение роутера /orgchart...")
api_router.include_router(
    orgchart.router, 
    prefix="/orgchart", # Префикс для всех путей в этом роутере
    tags=["orgchart"]   # Тег для документации Swagger/OpenAPI
)
# --------------------------------------

logging.info("--- Все роутеры подключены к api_router ---") 