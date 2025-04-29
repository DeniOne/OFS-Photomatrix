from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=schemas.UsersPublic)
async def read_users(
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    \"\"\"Retrieve users (Superuser only).\"\"\"
    # Используем синхронный CRUD внутри run_sync
    users = await deps.run_sync(crud.user.get_multi_paginated)(db, skip=skip, limit=limit)
    count = await deps.run_sync(crud.user.get_count)(db)
    return {"data": users, "total": count}

@router.post("/", response_model=schemas.User)
async def create_user(
    *, 
    db: AsyncSession = Depends(deps.get_async_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    \"\"\"Create new user (Superuser only).\"\"\"
    user = await deps.run_sync(crud.user.get_by_email)(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await deps.run_sync(crud.user.create)(db, obj_in=user_in)
    return user

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    \"\"\"Get current user.\"\"\"
    return current_user

@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *, 
    db: AsyncSession = Depends(deps.get_async_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: str = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    \"\"\"Update own user.\"\"\"
    current_user_data = current_user.__dict__ # Преобразуем модель в словарь
    user_in = schemas.UserUpdate(**current_user_data) # Создаем схему из словаря
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
        
    # Проверка, если email уже занят другим пользователем
    if email:
         existing_user = await deps.run_sync(crud.user.get_by_email)(db, email=email)
         if existing_user and existing_user.id != current_user.id:
             raise HTTPException(status_code=400, detail="Email already registered by another user.")

    user = await deps.run_sync(crud.user.update)(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_async_db),
) -> Any:
    \"\"\"Get a specific user by id (Superuser only).\"\"\"
    user = await deps.run_sync(crud.user.get)(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    return user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    *, 
    db: AsyncSession = Depends(deps.get_async_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    \"\"\"Update a user (Superuser only).\"\"\"
    user = await deps.run_sync(crud.user.get)(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
        
    # Проверка, если email уже занят другим пользователем
    if user_in.email:
         existing_user = await deps.run_sync(crud.user.get_by_email)(db, email=user_in.email)
         if existing_user and existing_user.id != user_id:
             raise HTTPException(status_code=400, detail="Email already registered by another user.")
             
    user = await deps.run_sync(crud.user.update)(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(
    *, 
    db: AsyncSession = Depends(deps.get_async_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    \"\"\"Delete a user (Superuser only).\"\"\"
    user = await deps.run_sync(crud.user.get)(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Нельзя удалить самого себя или другого суперюзера, если ты не суперюзер (хотя проверка уже есть)
    if user.id == current_user.id:
         raise HTTPException(status_code=403, detail="Users are not allowed to delete themselves")
    # Опционально: добавить проверку, чтобы суперюзеры не могли удалять друг друга
    # if user.is_superuser and not current_user.is_superuser: # Это условие неверно, т.к. текущий уже суперюзер
    #     raise HTTPException(status_code=403, detail="Superusers cannot delete other superusers") # Логику можно усложнить
        
    deleted_user = await deps.run_sync(crud.user.remove)(db, id=user_id)
    return deleted_user 