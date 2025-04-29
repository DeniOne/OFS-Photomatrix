from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.Division)
async def create_division(
    *,
    db: AsyncSession = Depends(deps.get_db),
    division_in: schemas.DivisionCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Division:
    """Создание нового подразделения"""
    division = await crud.division.create(db=db, obj_in=division_in)
    return division

@router.get("/", response_model=List[schemas.Division])
async def read_divisions(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> List[models.Division]:
    """Получение списка подразделений"""
    divisions = await crud.division.get_multi(db, skip=skip, limit=limit)
    return divisions

@router.get("/{division_id}", response_model=schemas.Division)
async def read_division(
    *,
    db: AsyncSession = Depends(deps.get_db),
    division_id: int,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> models.Division:
    """Получение информации о подразделении по ID"""
    division = await crud.division.get(db=db, id=division_id)
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")
    return division

@router.put("/{division_id}", response_model=schemas.Division)
async def update_division(
    *,
    db: AsyncSession = Depends(deps.get_db),
    division_id: int,
    division_in: schemas.DivisionUpdate,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Division:
    """Обновление информации о подразделении"""
    division = await crud.division.get(db=db, id=division_id)
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")
    updated_division = await crud.division.update(db=db, db_obj=division, obj_in=division_in)
    return updated_division

@router.delete("/{division_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_division(
    *,
    db: AsyncSession = Depends(deps.get_db),
    division_id: int,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> None:
    """Удаление подразделения"""
    division = await crud.division.get(db=db, id=division_id)
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")
    
    await crud.division.remove(db=db, id=division_id)
    return None 