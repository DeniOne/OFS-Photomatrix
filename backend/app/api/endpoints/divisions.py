from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app import crud
from app.api import deps
from app.db.base import get_db
from app.schemas import division as schemas
from app.models import user as models

router = APIRouter()

@router.get("/", response_model=List[schemas.Division])
async def read_divisions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[int] = Query(None, description="Фильтр по ID организации"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Получить список всех подразделений с возможностью фильтрации по организации"""
    divisions = await crud.division.get_divisions(
        db=db, skip=skip, limit=limit, organization_id=organization_id
    )
    return divisions

@router.post("/", response_model=schemas.Division, status_code=status.HTTP_201_CREATED)
async def create_division(
    *,
    db: AsyncSession = Depends(get_db),
    division_in: schemas.DivisionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Создать новое подразделение"""
    # Проверяем существование организации
    organization = await crud.organization.get(db=db, id=division_in.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Организация с ID {division_in.organization_id} не найдена",
        )
    
    # Проверяем существование родительского подразделения, если указано
    if division_in.parent_id:
        parent = await crud.division.get_division(db=db, division_id=division_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Родительское подразделение с ID {division_in.parent_id} не найдено",
            )
        # Проверяем, что родительское подразделение принадлежит той же организации
        if parent.organization_id != division_in.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Родительское подразделение должно принадлежать той же организации",
            )
    
    division = await crud.division.create_division(db=db, division_in=division_in)
    return division

@router.get("/{division_id}", response_model=schemas.Division)
async def read_division(
    *,
    db: AsyncSession = Depends(get_db),
    division_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Получить подразделение по ID"""
    division = await crud.division.get_division(db=db, division_id=division_id)
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подразделение не найдено",
        )
    return division

@router.put("/{division_id}", response_model=schemas.Division)
async def update_division(
    *,
    db: AsyncSession = Depends(get_db),
    division_id: int,
    division_in: schemas.DivisionUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Обновить подразделение"""
    division = await crud.division.get_division(db=db, division_id=division_id)
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подразделение не найдено",
        )
    
    # Если изменяется родительское подразделение, проверяем его существование и принадлежность к организации
    if division_in.parent_id is not None and division_in.parent_id != division.parent_id:
        if division_in.parent_id > 0:
            parent = await crud.division.get_division(db=db, division_id=division_in.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Родительское подразделение с ID {division_in.parent_id} не найдено",
                )
            
            # Определяем ID организации - берем либо из обновления, либо из текущего объекта
            organization_id = division_in.organization_id or division.organization_id
            
            # Проверяем, что родительское подразделение принадлежит той же организации
            if parent.organization_id != organization_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Родительское подразделение должно принадлежать той же организации",
                )
    
    # Если изменяется организация, проверяем ее существование
    if division_in.organization_id is not None and division_in.organization_id != division.organization_id:
        organization = await crud.organization.get(db=db, id=division_in.organization_id)
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Организация с ID {division_in.organization_id} не найдена",
            )
    
    division = await crud.division.update_division(db=db, db_obj=division, obj_in=division_in)
    return division

@router.delete("/{division_id}", response_model=schemas.Division)
async def delete_division(
    *,
    db: AsyncSession = Depends(get_db),
    division_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Удалить подразделение"""
    division = await crud.division.get_division(db=db, division_id=division_id)
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подразделение не найдено",
        )
    
    # Проверяем наличие дочерних подразделений
    query = select(models.Division).filter(models.Division.parent_id == division_id)
    result = await db.execute(query)
    children = result.scalars().all()
    if len(children) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить подразделение, имеющее дочерние подразделения",
        )
    
    division = await crud.division.delete_division(db=db, division_id=division_id)
    return division

@router.get("/organization/{organization_id}/tree", response_model=List[schemas.DivisionWithRelations])
async def read_organization_division_tree(
    *,
    db: AsyncSession = Depends(get_db),
    organization_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Получить иерархическое дерево подразделений организации"""
    # Проверяем существование организации
    organization = await crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Организация с ID {organization_id} не найдена",
        )
    
    division_tree = await crud.division.get_division_tree(db=db, organization_id=organization_id)
    return division_tree 