from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.functional_relation import FunctionalRelation
from app.schemas.functional_relation import FunctionalRelationCreate, FunctionalRelationUpdate

class CRUDFunctionalRelation(CRUDBase[FunctionalRelation, FunctionalRelationCreate, FunctionalRelationUpdate]):
    """CRUD для работы с функциональными отношениями между должностями"""
    
    async def get_by_source_and_target(
        self, db: AsyncSession, *, source_id: int, target_id: int
    ) -> Optional[FunctionalRelation]:
        """
        Получить отношение по ID исходной и целевой должности
        """
        query = select(self.model).filter(
            self.model.source_id == source_id,
            self.model.target_id == target_id
        )
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_position(
        self, db: AsyncSession, *, position_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все отношения для должности (как исходной, так и целевой)
        """
        query = select(self.model).filter(
            or_(
                self.model.source_id == position_id,
                self.model.target_id == position_id
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_sources_for_target(
        self, db: AsyncSession, *, target_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все исходные отношения для целевой должности
        """
        query = select(self.model).filter(
            self.model.target_id == target_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_targets_for_source(
        self, db: AsyncSession, *, source_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalRelation]:
        """
        Получить все целевые отношения для исходной должности
        """
        query = select(self.model).filter(
            self.model.source_id == source_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

functional_relation = CRUDFunctionalRelation(FunctionalRelation) 