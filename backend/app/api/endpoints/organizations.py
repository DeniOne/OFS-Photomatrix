from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_active_user
from app.crud import organization as crud_organization
from app.models.user import User
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate, OrganizationWithChildren

router = APIRouter()

@router.get("/", response_model=List[Organization])
async def read_organizations(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    org_type: Optional[str] = Query(None, description="Фильтр по типу организации"),
    parent_id: Optional[int] = Query(None, description="Фильтр по родительской организации"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить список организаций с возможностью фильтрации
    """
    # print("--- DEBUG: Hitting restored read_organizations endpoint ---") # Оставляем для отладки, если понадобится
    if org_type:
        organizations = await crud_organization.get_by_type(
            db, org_type=org_type, skip=skip, limit=limit
        )
    elif parent_id is not None:
        organizations = await crud_organization.get_multi_by_parent(
            db, parent_id=parent_id, skip=skip, limit=limit
        )
    else:
        organizations = await crud_organization.get_multi(
            db=db, skip=skip, limit=limit
        )
    return organizations

@router.get("/tree", response_model=List[OrganizationWithChildren])
async def read_organization_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить дерево организаций
    """
    return await crud_organization.get_tree(db)

@router.get("/root", response_model=List[Organization])
async def read_root_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить корневые организации (без родителя)
    """
    return await crud_organization.get_root_organizations(db)

@router.post("/", response_model=Organization, status_code=status.HTTP_201_CREATED)
async def create_organization(
    *,
    db: AsyncSession = Depends(get_db),
    organization_in: OrganizationCreate,
    # current_user: User = Depends(get_current_active_user),  # Временно отключаем проверку аутентификации
) -> Any:
    """
    Создать новую организацию
    """
    # Проверяем существование кода
    organization = await crud_organization.get_by_code(db, code=organization_in.code)
    if organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Организация с таким кодом уже существует",
        )
        
    # Проверяем существование родительской организации, если указана
    if organization_in.parent_id:
        parent = await crud_organization.get(db, id=organization_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительская организация не найдена",
            )
            
    return await crud_organization.create(db, obj_in=organization_in)

@router.get("/{id}", response_model=Organization)
async def read_organization(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить организацию по ID
    """
    organization = await crud_organization.get(db, id=id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )
    return organization

@router.get("/{id}/with-children", response_model=OrganizationWithChildren)
async def read_organization_with_children(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить организацию с дочерними организациями
    """
    organization = await crud_organization.get_with_children(db, id=id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )
    return organization

@router.put("/{id}", response_model=Organization)
async def update_organization(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    organization_in: OrganizationUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить организацию
    """
    organization = await crud_organization.get(db, id=id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )
        
    # Если меняется родитель, проверяем его существование
    if organization_in.parent_id and organization_in.parent_id != organization.parent_id:
        parent = await crud_organization.get(db, id=organization_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительская организация не найдена",
            )
            
    return await crud_organization.update(db, db_obj=organization, obj_in=organization_in)

@router.delete("/{id}", response_model=Organization)
async def delete_organization(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить организацию
    """
    organization = await crud_organization.get(db, id=id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )
        
    # Здесь можно добавить дополнительные проверки, например, на наличие дочерних организаций
    
    return await crud_organization.remove(db, id=id) 