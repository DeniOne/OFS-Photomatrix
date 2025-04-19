from typing import List, Optional, Dict, Any
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate

class CRUDStaff(CRUDBase[Staff, StaffCreate, StaffUpdate]):
    """CRUD для работы с сотрудниками"""
    
    async def get_by_email(
        self, db: AsyncSession, *, email: str
    ) -> Optional[Staff]:
        """
        Получить сотрудника по email
        """
        query = select(self.model).filter(self.model.email == email)
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_user_id(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[Staff]:
        """
        Получить сотрудника по ID пользователя
        """
        query = select(self.model).filter(self.model.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().first()
        
    async def search(
        self, db: AsyncSession, *, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[Staff]:
        """
        Поиск сотрудников по имени или фамилии
        """
        search_pattern = f"%{search_term}%"
        query = select(self.model).filter(
            or_(
                self.model.first_name.ilike(search_pattern),
                self.model.last_name.ilike(search_pattern)
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

staff = CRUDStaff(Staff) 