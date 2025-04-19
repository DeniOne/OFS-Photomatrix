from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.function import Function
from app.schemas.function import FunctionCreate, FunctionUpdate

class CRUDFunction(CRUDBase[Function, FunctionCreate, FunctionUpdate]):
    """CRUD для работы с функциями"""
    
    async def get_by_code(
        self, db: AsyncSession, *, code: str
    ) -> Optional[Function]:
        """
        Получить функцию по коду
        """
        query = select(self.model).filter(self.model.code == code)
        result = await db.execute(query)
        return result.scalars().first()
        
    async def search(
        self, db: AsyncSession, *, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[Function]:
        """
        Поиск функций по названию
        """
        search_pattern = f"%{search_term}%"
        query = select(self.model).filter(
            self.model.name.ilike(search_pattern)
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

function = CRUDFunction(Function) 