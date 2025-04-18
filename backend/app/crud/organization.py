from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    """CRUD операции для организаций"""
    
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Organization]:
        """Получить организацию по коду"""
        query = select(Organization).filter(Organization.code == code)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_multi_by_parent(
        self, db: AsyncSession, *, parent_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """Получить организации по родительской организации"""
        query = select(Organization).filter(Organization.parent_id == parent_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_type(
        self, db: AsyncSession, *, org_type: str, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        """Получить организации по типу"""
        query = select(Organization).filter(Organization.org_type == org_type).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_with_children(self, db: AsyncSession, *, id: int) -> Optional[Organization]:
        """Получить организацию с дочерними организациями"""
        query = select(Organization).options(selectinload(Organization.children)).filter(Organization.id == id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_root_organizations(self, db: AsyncSession) -> List[Organization]:
        """Получить корневые организации (без родителя)"""
        query = select(Organization).filter(Organization.parent_id == None)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_tree(self, db: AsyncSession) -> List[Organization]:
        """Получить дерево организаций"""
        query = select(Organization).options(selectinload(Organization.children)).filter(Organization.parent_id == None)
        result = await db.execute(query)
        return result.scalars().all()

# Создание синглтона для использования в приложении
organization = CRUDOrganization(Organization) 