from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.section import Section
from app.schemas.section import SectionCreate, SectionUpdate

class CRUDSection(CRUDBase[Section, SectionCreate, SectionUpdate]):
    """CRUD для работы с отделами"""
    
    async def get_by_code_and_division(
        self, db: AsyncSession, *, code: str, division_id: int
    ) -> Optional[Section]:
        """
        Получить отдел по коду и ID подразделения
        """
        query = select(self.model).filter(
            self.model.code == code, 
            self.model.division_id == division_id
        )
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_division(
        self, db: AsyncSession, *, division_id: int, skip: int = 0, limit: int = 100
    ) -> List[Section]:
        """
        Получить все отделы подразделения
        """
        query = select(self.model).filter(
            self.model.division_id == division_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

section = CRUDSection(Section) 