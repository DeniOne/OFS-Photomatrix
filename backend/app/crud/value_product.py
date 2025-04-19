from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.value_product import ValueProduct
from app.schemas.value_product import ValueProductCreate, ValueProductUpdate

class CRUDValueProduct(CRUDBase[ValueProduct, ValueProductCreate, ValueProductUpdate]):
    """CRUD для работы с ЦКП (Ценными Конечными Продуктами)"""
    
    async def get_by_code_and_org(
        self, db: AsyncSession, *, code: str, organization_id: int
    ) -> Optional[ValueProduct]:
        """
        Получить ЦКП по коду и ID организации
        """
        query = select(self.model).filter(
            self.model.code == code, 
            self.model.organization_id == organization_id
        )
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_organization(
        self, db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[ValueProduct]:
        """
        Получить все ЦКП организации
        """
        query = select(self.model).filter(
            self.model.organization_id == organization_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_root_value_products(
        self, db: AsyncSession, *, organization_id: int
    ) -> List[ValueProduct]:
        """
        Получить корневые ЦКП (без родителя)
        """
        query = select(self.model).filter(
            self.model.organization_id == organization_id,
            self.model.parent_id == None
        )
        result = await db.execute(query)
        return result.scalars().all()

value_product = CRUDValueProduct(ValueProduct) 