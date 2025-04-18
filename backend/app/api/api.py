from fastapi import APIRouter

from app.api.endpoints import auth, users, organizations

api_router = APIRouter()

# Группировка по API эндпоинтам
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"]) 