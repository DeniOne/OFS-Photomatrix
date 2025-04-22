from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, join
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.functional_assignment import FunctionalAssignment
from app.models.position import Position
from app.models.function import Function
from app.schemas.functional_assignment import FunctionalAssignmentCreate, FunctionalAssignmentUpdate

class CRUDFunctionalAssignment(CRUDBase[FunctionalAssignment, FunctionalAssignmentCreate, FunctionalAssignmentUpdate]):
    """CRUD для работы с назначениями функций на должности"""
    
    async def get_by_position_and_function(
        self, db: AsyncSession, *, position_id: int, function_id: int
    ) -> Optional[FunctionalAssignment]:
        """
        Получить назначение по ID должности и функции
        """
        query = select(self.model).filter(
            self.model.position_id == position_id,
            self.model.function_id == function_id
        )
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_position(
        self, db: AsyncSession, *, position_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalAssignment]:
        """
        Получить все функции должности
        """
        query = select(self.model).filter(
            self.model.position_id == position_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_by_function(
        self, db: AsyncSession, *, function_id: int, skip: int = 0, limit: int = 100
    ) -> List[FunctionalAssignment]:
        """
        Получить все должности с данной функцией
        """
        query = select(self.model).filter(
            self.model.function_id == function_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_functions_for_division(
        self, db: AsyncSession, *, division_id: int, skip: int = 0, limit: int = 100
    ) -> List[Function]:
        """
        Получить все функции, назначенные на должности в указанном подразделении
        """
        # Создаем запрос для получения функций через связанные таблицы
        query = select(Function).distinct().join(
            FunctionalAssignment, FunctionalAssignment.function_id == Function.id
        ).join(
            Position, FunctionalAssignment.position_id == Position.id
        ).filter(
            Position.division_id == division_id
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

functional_assignment = CRUDFunctionalAssignment(FunctionalAssignment) 