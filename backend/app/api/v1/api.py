from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, organization, division, section, position, staff # Добавил staff

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organization.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(division.router, prefix="/divisions", tags=["divisions"])
api_router.include_router(section.router, prefix="/sections", tags=["sections"])
api_router.include_router(position.router, prefix="/positions", tags=["positions"])
api_router.include_router(staff.router, prefix="/staff", tags=["staff"]) # Добавил staff 