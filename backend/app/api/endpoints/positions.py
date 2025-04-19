from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_active_user
from app.crud import position as crud_position
from app.crud import section as crud_section
from app.models.user import User
from app.schemas.position import Position, PositionCreate, PositionUpdate

router = APIRouter()

@router.get("/", response_model=List[Position])
async def read_positions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    section_id: Optional[int] = Query(None, description="Фильтр по отделу"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить список должностей с возможностью фильтрации
    """
    if section_id:
        positions = await crud_position.position.get_by_section(
            db, section_id=section_id, skip=skip, limit=limit
        )
    else:
        positions = await crud_position.position.get_multi(
            db, skip=skip, limit=limit
        )
    return positions

@router.post("/", response_model=Position)
async def create_position(
    *,
    db: AsyncSession = Depends(get_db),
    position_in: PositionCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Создать новую должность
    """
    # Проверяем существование отдела
    section = await crud_section.section.get(db, id=position_in.section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отдел не найден",
        )
        
    # Проверяем уникальность кода в рамках отдела
    existing_position = await crud_position.position.get_by_code_and_section(
        db, code=position_in.code, section_id=position_in.section_id
    )
    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Должность с таким кодом уже существует в данном отделе",
        )
            
    return await crud_position.position.create(db, obj_in=position_in)

@router.get("/{id}", response_model=Position)
async def read_position(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить должность по ID
    """
    position = await crud_position.position.get(db, id=id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Должность не найдена",
        )
    return position

@router.put("/{id}", response_model=Position)
async def update_position(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    position_in: PositionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить должность
    """
    position = await crud_position.position.get(db, id=id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Должность не найдена",
        )
        
    # Если меняется отдел или код, проверяем уникальность кода в рамках отдела
    if (position_in.code and position_in.code != position.code) or \
       (position_in.section_id and position_in.section_id != position.section_id):
        section_id = position_in.section_id or position.section_id
        code = position_in.code or position.code
        existing_position = await crud_position.position.get_by_code_and_section(
            db, code=code, section_id=section_id
        )
        if existing_position and existing_position.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Должность с таким кодом уже существует в данном отделе",
            )
            
    # Если меняется отдел, проверяем его существование
    if position_in.section_id and position_in.section_id != position.section_id:
        section = await crud_section.section.get(db, id=position_in.section_id)
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отдел не найден",
            )
            
    return await crud_position.position.update(db, db_obj=position, obj_in=position_in)

@router.delete("/{id}", response_model=Position)
async def delete_position(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить должность
    """
    position = await crud_position.position.get(db, id=id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Должность не найдена",
        )
        
    # Здесь можно добавить дополнительные проверки, например, наличие сотрудников на данной должности
    
    return await crud_position.position.remove(db, id=id) 