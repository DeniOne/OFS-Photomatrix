from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import time
import logging

from app.crud.base import CRUDBase
from app.models.division import Division
from app.schemas.division import DivisionCreate, DivisionUpdate

# Получаем логгер
logger = logging.getLogger(__name__)

class CRUDDivision(CRUDBase[Division, DivisionCreate, DivisionUpdate]):
    """CRUD для работы с подразделениями"""
    
    async def get_by_code_and_org(
        self, db: AsyncSession, *, code: str, organization_id: int
    ) -> Optional[Division]:
        """
        Получить подразделение по коду и ID организации
        """
        start_time = time.time()
        query = select(self.model).filter(
            self.model.code == code, 
            self.model.organization_id == organization_id
        )
        result = await db.execute(query)
        division = result.scalars().first()
        query_time = time.time() - start_time
        logger.info(f"get_by_code_and_org выполнен за {query_time:.4f}s")
        return division
        
    async def get_by_organization(
        self, db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Division]:
        """
        Получить все подразделения организации
        """
        start_time = time.time()
        query = select(self.model).filter(
            self.model.organization_id == organization_id
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        divisions = result.scalars().all()
        query_time = time.time() - start_time
        logger.info(f"get_by_organization получил {len(divisions)} записей за {query_time:.4f}s")
        return divisions
        
    async def get_root_divisions(
        self, db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Division]:
        """
        Получить корневые подразделения организации (без родителей)
        """
        start_time = time.time()
        query = select(self.model).filter(
            self.model.organization_id == organization_id,
            self.model.parent_id == None
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        divisions = result.scalars().all()
        query_time = time.time() - start_time
        logger.info(f"get_root_divisions получил {len(divisions)} записей за {query_time:.4f}s")
        return divisions
        
    async def get_divisions(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        organization_id: Optional[int] = None
    ) -> List[Division]:
        """Получить список подразделений с возможностью фильтрации по организации"""
        start_time = time.time()
        query = select(self.model)
        
        if organization_id is not None:
            query = query.filter(self.model.organization_id == organization_id)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        divisions = result.scalars().all()
        query_time = time.time() - start_time
        logger.info(f"get_divisions получил {len(divisions)} записей за {query_time:.4f}s")
        return divisions
    
    async def get_division(self, db: AsyncSession, division_id: int) -> Optional[Division]:
        """Получить подразделение по ID"""
        start_time = time.time()
        query = select(self.model).filter(self.model.id == division_id)
        result = await db.execute(query)
        division = result.scalars().first()
        query_time = time.time() - start_time
        logger.info(f"get_division ID={division_id} выполнен за {query_time:.4f}s")
        return division
    
    async def create_division(self, db: AsyncSession, division_in: DivisionCreate) -> Division:
        """Создать новое подразделение"""
        start_time = time.time()
        obj_in_data = jsonable_encoder(division_in)
        db_division = self.model(**obj_in_data)
        db.add(db_division)
        await db.commit()
        await db.refresh(db_division)
        create_time = time.time() - start_time
        logger.info(f"create_division создал запись ID={db_division.id} за {create_time:.4f}s")
        return db_division

    async def update_division(
        self,
        db: AsyncSession, 
        db_obj: Division,
        obj_in: Union[DivisionUpdate, Dict[str, Any]]
    ) -> Division:
        """Обновить подразделение"""
        start_time = time.time()
        obj_data = jsonable_encoder(db_obj)
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        update_time = time.time() - start_time
        logger.info(f"update_division обновил запись ID={db_obj.id} за {update_time:.4f}s")
        return db_obj

    async def delete_division(self, db: AsyncSession, division_id: int) -> Division:
        """Удалить подразделение"""
        start_time = time.time()
        division = await self.get_division(db, division_id)
        if division:
            await db.delete(division)
            await db.commit()
        delete_time = time.time() - start_time
        logger.info(f"delete_division удалил запись ID={division_id} за {delete_time:.4f}s")
        return division

    async def get_division_tree(self, db: AsyncSession, organization_id: int) -> List[Division]:
        """
        Получить дерево подразделений для организации
        Возвращает список корневых подразделений с вложенными дочерними
        """
        start_time = time.time()
        query = select(self.model).filter(
            self.model.organization_id == organization_id,
            self.model.parent_id.is_(None)
        )
        result = await db.execute(query)
        divisions = result.scalars().all()
        query_time = time.time() - start_time
        logger.info(f"get_division_tree получил {len(divisions)} корневых записей за {query_time:.4f}s")
        return divisions

# Создаем экземпляр для работы с division
division = CRUDDivision(Division) 