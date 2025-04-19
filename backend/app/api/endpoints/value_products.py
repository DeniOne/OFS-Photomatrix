from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_active_user
from app.crud import value_product as crud_value_product
from app.crud import organization as crud_organization
from app.models.user import User
from app.schemas.value_product import ValueProduct, ValueProductCreate, ValueProductUpdate, ValueProductWithChildren

router = APIRouter()

@router.get("/", response_model=List[ValueProduct])
async def read_value_products(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[int] = Query(None, description="Фильтр по организации"),
    parent_id: Optional[int] = Query(None, description="Фильтр по родительскому ЦКП"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить список ЦКП с возможностью фильтрации
    """
    if organization_id:
        value_products = await crud_value_product.value_product.get_by_organization(
            db, organization_id=organization_id, skip=skip, limit=limit
        )
    elif parent_id is not None:
        # Временно используем стандартный фильтр, в будущем можно добавить метод в CRUD
        value_products = await crud_value_product.value_product.get_multi(
            db, skip=skip, limit=limit
        )
        value_products = [vp for vp in value_products if vp.parent_id == parent_id]
    else:
        value_products = await crud_value_product.value_product.get_multi(
            db, skip=skip, limit=limit
        )
    return value_products

@router.get("/root", response_model=List[ValueProduct])
async def read_root_value_products(
    db: AsyncSession = Depends(get_db),
    organization_id: Optional[int] = Query(None, description="ID организации"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить корневые ЦКП (без родителя)
    """
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать ID организации",
        )
    return await crud_value_product.value_product.get_root_value_products(db, organization_id=organization_id)

@router.post("/", response_model=ValueProduct)
async def create_value_product(
    *,
    db: AsyncSession = Depends(get_db),
    value_product_in: ValueProductCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Создать новый ЦКП
    """
    # Проверяем существование организации
    organization = await crud_organization.organization.get(db, id=value_product_in.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )
        
    # Проверяем уникальность кода в рамках организации
    existing_value_product = await crud_value_product.value_product.get_by_code_and_org(
        db, code=value_product_in.code, organization_id=value_product_in.organization_id
    )
    if existing_value_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ЦКП с таким кодом уже существует в данной организации",
        )
        
    # Проверяем существование родительского ЦКП, если указан
    if value_product_in.parent_id:
        parent = await crud_value_product.value_product.get(db, id=value_product_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительский ЦКП не найден",
            )
            
    return await crud_value_product.value_product.create(db, obj_in=value_product_in)

@router.get("/{id}", response_model=ValueProduct)
async def read_value_product(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить ЦКП по ID
    """
    value_product = await crud_value_product.value_product.get(db, id=id)
    if not value_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ЦКП не найден",
        )
    return value_product

@router.put("/{id}", response_model=ValueProduct)
async def update_value_product(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    value_product_in: ValueProductUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить ЦКП
    """
    value_product = await crud_value_product.value_product.get(db, id=id)
    if not value_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ЦКП не найден",
        )
        
    # Если меняется организация или код, проверяем уникальность кода в рамках организации
    if (value_product_in.code and value_product_in.code != value_product.code) or \
       (value_product_in.organization_id and value_product_in.organization_id != value_product.organization_id):
        org_id = value_product_in.organization_id or value_product.organization_id
        code = value_product_in.code or value_product.code
        existing_value_product = await crud_value_product.value_product.get_by_code_and_org(
            db, code=code, organization_id=org_id
        )
        if existing_value_product and existing_value_product.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ЦКП с таким кодом уже существует в данной организации",
            )
            
    # Если меняется родитель, проверяем его существование
    if value_product_in.parent_id and value_product_in.parent_id != value_product.parent_id:
        parent = await crud_value_product.value_product.get(db, id=value_product_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительский ЦКП не найден",
            )
            
    return await crud_value_product.value_product.update(db, db_obj=value_product, obj_in=value_product_in)

@router.delete("/{id}", response_model=ValueProduct)
async def delete_value_product(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить ЦКП
    """
    value_product = await crud_value_product.value_product.get(db, id=id)
    if not value_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ЦКП не найден",
        )
        
    # Здесь можно добавить дополнительные проверки, например, на наличие дочерних ЦКП
    # или связей с другими сущностями (эта часть будет реализована позже)
    
    return await crud_value_product.value_product.remove(db, id=id) 