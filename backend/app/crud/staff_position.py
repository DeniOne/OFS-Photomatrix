from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.staff_position import StaffPosition
from app.schemas.staff_position import StaffPositionCreate, StaffPositionUpdate

class CRUDStaffPosition(CRUDBase[StaffPosition, StaffPositionCreate, StaffPositionUpdate]):
    """CRUD для работы с назначениями сотрудников на должности"""
    
    async def get_by_staff_and_position(
        self, db: AsyncSession, *, staff_id: int, position_id: int
    ) -> Optional[StaffPosition]:
        """
        Получить назначение по ID сотрудника и должности
        """
        query = select(self.model).filter(
            self.model.staff_id == staff_id,
            self.model.position_id == position_id
        )
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_staff(
        self, db: AsyncSession, *, staff_id: int, skip: int = 0, limit: int = 100
    ) -> List[StaffPosition]:
        """
        Получить все назначения сотрудника
        """
        query = select(self.model).filter(
            self.model.staff_id == staff_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_by_position(
        self, db: AsyncSession, *, position_id: int, skip: int = 0, limit: int = 100
    ) -> List[StaffPosition]:
        """
        Получить всех сотрудников на данной должности
        """
        query = select(self.model).filter(
            self.model.position_id == position_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_primary_position(
        self, db: AsyncSession, *, staff_id: int
    ) -> Optional[StaffPosition]:
        """
        Получить основную должность сотрудника
        """
        query = select(self.model).filter(
            self.model.staff_id == staff_id,
            self.model.is_primary == True
        )
        result = await db.execute(query)
        return result.scalars().first()

staff_position = CRUDStaffPosition(StaffPosition) 