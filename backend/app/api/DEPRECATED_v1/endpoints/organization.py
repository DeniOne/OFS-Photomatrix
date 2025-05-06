from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.Organization)
async def create_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_in: schemas.OrganizationCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Organization:
    """Создание новой организации"""
    organization = await crud.organization.create(db=db, obj_in=organization_in)
    return organization

@router.get("/", response_model=List[schemas.Organization])
async def read_organizations(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> List[models.Organization]:
    """Получение списка организаций"""
    organizations = await crud.organization.get_multi(db, skip=skip, limit=limit)
    return organizations

@router.get("/tree", response_model=List[schemas.OrganizationTree])
async def get_organization_tree(
    db: AsyncSession = Depends(deps.get_db),
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> List[schemas.OrganizationTree]:
    """Получение дерева организаций"""
    try:
        # Получаем все организации
        organizations = await crud.organization.get_all(db)
        
        # Строим дерево
        tree = []
        org_map = {org.id: org for org in organizations}
        
        # Собираем корневые узлы (без parent_id)
        for org in organizations:
            if org.parent_id is None:
                # Рекурсивно строим дерево
                tree_node = schemas.OrganizationTree.model_validate(org)
                tree_node.children = _build_children(org.id, org_map)
                tree.append(tree_node)
        
        return tree
    except Exception as e:
        logger.error(f"Error building organization tree: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error building organization tree: {str(e)}"
        )

def _build_children(parent_id: int, org_map: dict):
    """Рекурсивное построение дерева организаций"""
    children = []
    for org_id, org in org_map.items():
        if org.parent_id == parent_id:
            tree_node = schemas.OrganizationTree.model_validate(org)
            tree_node.children = _build_children(org.id, org_map)
            children.append(tree_node)
    return children

@router.get("/{organization_id}", response_model=schemas.Organization)
async def read_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> models.Organization:
    """Получение информации об организации по ID"""
    organization = await crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization

@router.put("/{organization_id}", response_model=schemas.Organization)
async def update_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    organization_in: schemas.OrganizationUpdate,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Organization:
    """Обновление информации об организации"""
    organization = await crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    updated_organization = await crud.organization.update(db=db, db_obj=organization, obj_in=organization_in)
    return updated_organization

@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> None:
    """Удаление организации"""
    organization = await crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    
    await crud.organization.remove(db=db, id=organization_id)
    return None 