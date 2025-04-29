from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.Section)
async def create_section(
    *,
    db: AsyncSession = Depends(deps.get_db),
    section_in: schemas.SectionCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Section:
    """Создание нового раздела"""
    section = await crud.section.create(db=db, obj_in=section_in)
    return section

@router.get("/", response_model=List[schemas.Section])
async def read_sections(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> List[models.Section]:
    """Получение списка разделов"""
    sections = await crud.section.get_multi(db, skip=skip, limit=limit)
    return sections

@router.get("/{section_id}", response_model=schemas.Section)
async def read_section(
    *,
    db: AsyncSession = Depends(deps.get_db),
    section_id: int,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> models.Section:
    """Получение информации о разделе по ID"""
    section = await crud.section.get(db=db, id=section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return section

@router.put("/{section_id}", response_model=schemas.Section)
async def update_section(
    *,
    db: AsyncSession = Depends(deps.get_db),
    section_id: int,
    section_in: schemas.SectionUpdate,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Section:
    """Обновление информации о разделе"""
    section = await crud.section.get(db=db, id=section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    updated_section = await crud.section.update(db=db, db_obj=section, obj_in=section_in)
    return updated_section

@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    *,
    db: AsyncSession = Depends(deps.get_db),
    section_id: int,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> None:
    """Удаление раздела"""
    section = await crud.section.get(db=db, id=section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    
    await crud.section.remove(db=db, id=section_id)
    return None 