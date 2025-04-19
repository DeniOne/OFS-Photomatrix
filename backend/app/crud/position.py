from typing import List, Optional, Union
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.position import Position
from app.schemas.position import PositionCreate, PositionUpdate

class CRUDPosition(CRUDBase[Position, PositionCreate, PositionUpdate]):
    """CRUD для работы с должностями"""
    
    async def get_by_code_and_division(
        self, db: AsyncSession, *, code: str, division_id: int
    ) -> Optional[Position]:
        """
        Получить должность по коду и ID подразделения
        """
        query = select(self.model).filter(
            self.model.code == code, 
            self.model.division_id == division_id
        )
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_division_or_section(
        self, db: AsyncSession, *, division_id: Optional[int] = None, section_id: Optional[int] = None, 
        skip: int = 0, limit: int = 100
    ) -> List[Position]:
        """
        Получить должности по подразделению или отделу
        """
        filters = []
        if division_id is not None:
            filters.append(self.model.division_id == division_id)
        if section_id is not None:
            filters.append(self.model.section_id == section_id)
            
        if not filters:
            return await self.get_multi(db, skip=skip, limit=limit)
            
        query = select(self.model).filter(
            or_(*filters)
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

position = CRUDPosition(Position) 