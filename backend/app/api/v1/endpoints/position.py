from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload # Для жадной загрузки связей
from typing import List, Optional
import logging

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.Position, status_code=status.HTTP_201_CREATED)
async def create_position(
    *,
    db: AsyncSession = Depends(deps.get_db),
    position_in: schemas.PositionCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Position:
    """Создание новой должности"""
    position = await crud.position.create(db=db, obj_in=position_in)
    return position

@router.get("/", response_model=List[schemas.Position])
async def read_positions(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> List[models.Position]:
    """Получение списка должностей"""
    positions = await crud.position.get_multi(db, skip=skip, limit=limit)
    return positions

@router.get("/{position_id}", response_model=schemas.Position)
async def read_position(
    *,
    db: AsyncSession = Depends(deps.get_db),
    position_id: int,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> models.Position:
    """Получение информации о должности по ID"""
    position = await crud.position.get(db=db, id=position_id)
    if not position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position not found")
    return position

@router.put("/{position_id}", response_model=schemas.Position)
async def update_position(
    *,
    db: AsyncSession = Depends(deps.get_db),
    position_id: int,
    position_in: schemas.PositionUpdate,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Position:
    """Обновление информации о должности"""
    position = await crud.position.get(db=db, id=position_id)
    if not position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position not found")
    updated_position = await crud.position.update(db=db, db_obj=position, obj_in=position_in)
    return updated_position

@router.delete("/{position_id}", response_model=schemas.Position)
async def delete_position(
    *,
    db: AsyncSession = Depends(deps.get_db),
    position_id: int,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Position:
    """Удаление должности с проверкой связей и детальным сообщением об ошибке"""
    logger.info(f"Запрос на удаление должности с ID {position_id}")
    
    try:
        position = await crud.position.get(db=db, id=position_id)
        if not position:
            logger.warning(f"Должность с ID {position_id} не найдена")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Должность не найдена")
        
        logger.info(f"Проверяем зависимости для должности {position.name} (ID: {position_id})")
        error_details = []

        # Проверка связанных функциональных назначений
        logger.debug(f"Проверка функциональных назначений для должности {position_id}")
        func_query = (
            select(models.FunctionalAssignment)
            .options(selectinload(models.FunctionalAssignment.function))
            .where(models.FunctionalAssignment.position_id == position_id)
        )
        func_result = await db.execute(func_query)
        assignments = func_result.scalars().all()
        logger.debug(f"Найдено {len(assignments)} функциональных назначений")
        
        if assignments:
            func_names = [f"'{a.function.name}' (ID: {a.function.id})" for a in assignments if a.function]
            error_detail = f"Используется в функциональных назначениях: {', '.join(func_names)}"
            logger.info(error_detail)
            error_details.append(error_detail)

        # Проверка связанных сотрудников
        logger.debug(f"Проверка назначений сотрудников для должности {position_id}")
        staff_query = (
            select(models.StaffPosition)
            .options(selectinload(models.StaffPosition.staff))
            .where(models.StaffPosition.position_id == position_id)
        )
        staff_result = await db.execute(staff_query)
        staff_assignments = staff_result.scalars().all()
        logger.debug(f"Найдено {len(staff_assignments)} назначений сотрудников")
        
        if staff_assignments:
            staff_names = [f"'{s.staff.full_name()}' (ID: {s.staff.id})" for s in staff_assignments if s.staff]
            error_detail = f"Назначена сотрудникам: {', '.join(staff_names)}"
            logger.info(error_detail)
            error_details.append(error_detail)

        # Проверка функциональных отношений (связей между должностями)
        logger.debug(f"Проверка функциональных отношений для должности {position_id}")
        relations_query = (
            select(models.FunctionalRelation)
            .where(
                (models.FunctionalRelation.source_id == position_id) |
                (models.FunctionalRelation.target_id == position_id)
            )
        )
        relations_result = await db.execute(relations_query)
        relations = relations_result.scalars().all()
        logger.debug(f"Найдено {len(relations)} функциональных отношений")
        
        if relations:
            relation_details = []
            for relation in relations:
                if relation.source_id == position_id:
                    relation_details.append(f"Источник для связи с ID {relation.id} (тип: {relation.relation_type})")
                else:
                    relation_details.append(f"Цель для связи с ID {relation.id} (тип: {relation.relation_type})")
            
            error_detail = f"Участвует в функциональных отношениях: {', '.join(relation_details)}"
            logger.info(error_detail)
            error_details.append(error_detail)

        # Если есть зависимости, возвращаем ошибку 409 (Conflict)
        if error_details:
            error_message = f"Невозможно удалить должность '{position.name}'. Причины: {'; '.join(error_details)}."
            logger.warning(f"Отклонена попытка удалить должность {position_id}: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, # Используем 409 Conflict
                detail=error_message
            )

        # Удаляем должность, если проверки пройдены
        # Однако сначала нужно явно удалить все связанные записи
        # в таблицах functional_assignment и staff_position, 
        # так как у них ondelete='RESTRICT'
        logger.info(f"Начинаем удаление должности {position.name} (ID: {position_id})")
        
        # Явно удаляем все функциональные назначения, связанные с должностью
        if assignments:
            logger.debug(f"Удаляем {len(assignments)} функциональных назначений")
            for assignment in assignments:
                await db.delete(assignment)
            
        # Явно удаляем все назначения сотрудников, связанные с должностью
        if staff_assignments:
            logger.debug(f"Удаляем {len(staff_assignments)} назначений сотрудников")
            for staff_assignment in staff_assignments:
                await db.delete(staff_assignment)
                
        # Удаляем функциональные отношения
        if relations:
            logger.debug(f"Удаляем {len(relations)} функциональных отношений")
            for relation in relations:
                await db.delete(relation)

        # После удаления всех зависимостей, можем удалить саму должность
        await db.delete(position)
        await db.commit()
        
        logger.info(f"Должность с ID {position_id} ({position.name}) успешно удалена")
        return position
        
    except HTTPException:
        # Пробрасываем HTTP исключения дальше
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при удалении должности {position_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера при удалении должности: {str(e)}"
        )

@router.options("/{position_id}")
async def options_position(position_id: int):
    """
    CORS preflight handler для доступа к отдельной должности
    """
    return {} 