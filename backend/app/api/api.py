from fastapi import APIRouter

from app.api.endpoints import auth, users, organizations, divisions, sections, positions, value_products

api_router = APIRouter()

# Группировка по API эндпоинтам
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(divisions.router, prefix="/divisions", tags=["divisions"])
api_router.include_router(sections.router, prefix="/sections", tags=["sections"])
api_router.include_router(positions.router, prefix="/positions", tags=["positions"])
api_router.include_router(value_products.router, prefix="/value-products", tags=["value-products"]) 