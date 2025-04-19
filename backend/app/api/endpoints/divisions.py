from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_active_user
from app.crud import division as crud_division
from app.crud import organization as crud_organization
from app.models.user import User
from app.schemas.division import Division, DivisionCreate, DivisionUpdate, DivisionWithChildren

router = APIRouter()

@router.get("/", response_model=List[Division])
async def read_divisions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[int] = Query(None, description="Фильтр по организации"),
    parent_id: Optional[int] = Query(None, description="Фильтр по родительскому подразделению"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить список подразделений с возможностью фильтрации
    """
    if organization_id:
        divisions = await crud_division.division.get_by_organization(
            db, organization_id=organization_id, skip=skip, limit=limit
        )
    elif parent_id is not None:
        # Временно используем стандартный фильтр, в будущем можно добавить метод в CRUD
        divisions = await crud_division.division.get_multi(
            db, skip=skip, limit=limit
        )
        divisions = [d for d in divisions if d.parent_id == parent_id]
    else:
        divisions = await crud_division.division.get_multi(
            db, skip=skip, limit=limit
        )
    return divisions

@router.get("/root", response_model=List[Division])
async def read_root_divisions(
    db: AsyncSession = Depends(get_db),
    organization_id: Optional[int] = Query(None, description="ID организации"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить корневые подразделения (без родителя)
    """
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать ID организации",
        )
    return await crud_division.division.get_root_divisions(db, organization_id=organization_id)

@router.post("/", response_model=Division)
async def create_division(
    *,
    db: AsyncSession = Depends(get_db),
    division_in: DivisionCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Создать новое подразделение
    """
    # Проверяем существование организации
    organization = await crud_organization.organization.get(db, id=division_in.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )
        
    # Проверяем уникальность кода в рамках организации
    existing_division = await crud_division.division.get_by_code_and_org(
        db, code=division_in.code, organization_id=division_in.organization_id
    )
    if existing_division:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Подразделение с таким кодом уже существует в данной организации",
        )
        
    # Проверяем существование родительского подразделения, если указано
    if division_in.parent_id:
        parent = await crud_division.division.get(db, id=division_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительское подразделение не найдено",
            )
            
    return await crud_division.division.create(db, obj_in=division_in)

@router.get("/{id}", response_model=Division)
async def read_division(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить подразделение по ID
    """
    division = await crud_division.division.get(db, id=id)
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подразделение не найдено",
        )
    return division

@router.put("/{id}", response_model=Division)
async def update_division(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    division_in: DivisionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить подразделение
    """
    division = await crud_division.division.get(db, id=id)
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подразделение не найдено",
        )
        
    # Если меняется организация или код, проверяем уникальность кода в рамках организации
    if (division_in.code and division_in.code != division.code) or \
       (division_in.organization_id and division_in.organization_id != division.organization_id):
        org_id = division_in.organization_id or division.organization_id
        code = division_in.code or division.code
        existing_division = await crud_division.division.get_by_code_and_org(
            db, code=code, organization_id=org_id
        )
        if existing_division and existing_division.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Подразделение с таким кодом уже существует в данной организации",
            )
            
    # Если меняется родитель, проверяем его существование
    if division_in.parent_id and division_in.parent_id != division.parent_id:
        parent = await crud_division.division.get(db, id=division_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительское подразделение не найдено",
            )
            
    return await crud_division.division.update(db, db_obj=division, obj_in=division_in)

@router.delete("/{id}", response_model=Division)
async def delete_division(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить подразделение
    """
    division = await crud_division.division.get(db, id=id)
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подразделение не найдено",
        )
        
    # Здесь можно добавить дополнительные проверки, например, на наличие дочерних подразделений или отделов
    
    return await crud_division.division.remove(db, id=id) 