from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.base import get_db
from app.api.deps import get_current_active_user
from app import crud, models, schemas
from app.schemas.position import Position, PositionCreate, PositionUpdate
from app.models.functional_assignment import FunctionalAssignment

router = APIRouter()

@router.get("/", response_model=List[Position])
async def read_positions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    section_id: Optional[int] = Query(None, description="Фильтр по отделу"),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить список должностей с возможностью фильтрации
    """
    if section_id:
        positions = await crud.position.get_by_section(
            db, section_id=section_id, skip=skip, limit=limit
        )
    else:
        positions = await crud.position.get_multi(
            db, skip=skip, limit=limit
        )
    
    # Добавляем информацию о связанных функциях
    for position in positions:
        # Получаем все функциональные назначения для должности
        query = select(FunctionalAssignment.function_id).where(FunctionalAssignment.position_id == position.id)
        result = await db.execute(query)
        # Создаем список ID функций
        position.function_ids = [function_id for function_id, in result]
        
    return positions

@router.post("/", response_model=Position)
async def create_position(
    *,
    db: AsyncSession = Depends(get_db),
    position_in: PositionCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Создать новую должность
    """
    # Проверяем существование отдела
    section = await crud.section.get(db, id=position_in.section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отдел не найден",
        )
        
    # Проверяем уникальность кода в рамках отдела
    existing_position = await crud.position.get_by_code_and_section(
        db, code=position_in.code, section_id=position_in.section_id
    )
    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Должность с таким кодом уже существует в данном отделе",
        )
    
    # Сохраняем ID функций перед созданием должности
    function_ids = position_in.function_ids
    
    # Создаем должность без function_ids (будут обрабатываться отдельно)
    position_data = position_in.dict(exclude={"function_ids"})
    position = await crud.position.create(db, obj_in=position_data)
    
    # Создаем функциональные назначения для новой должности
    if function_ids:
        for function_id in function_ids:
            # Проверяем существование функции
            function = await crud.function.get(db, id=function_id)
            if not function:
                # Откатываем транзакцию и выходим с ошибкой
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Функция с ID {function_id} не найдена",
                )
            
            # Создаем функциональное назначение
            assignment = FunctionalAssignment(
                position_id=position.id,
                function_id=function_id,
                is_primary=False  # По умолчанию не основная функция
            )
            db.add(assignment)
        
        # Сохраняем изменения
        await db.commit()
        
        # Добавляем ID функций в ответ
        position.function_ids = function_ids
    
    return position

@router.get("/{id}", response_model=Position)
async def read_position(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить должность по ID
    """
    position = await crud.position.get(db, id=id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Должность не найдена",
        )
    
    # Получаем все функциональные назначения для должности
    query = select(FunctionalAssignment.function_id).where(FunctionalAssignment.position_id == position.id)
    result = await db.execute(query)
    # Создаем список ID функций
    position.function_ids = [function_id for function_id, in result]
    
    return position

@router.put("/{id}", response_model=Position)
async def update_position(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    position_in: PositionUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить должность
    """
    position = await crud.position.get(db, id=id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Должность не найдена",
        )
        
    # Если меняется отдел или код, проверяем уникальность кода в рамках отдела
    if (position_in.code and position_in.code != position.code) or \
       (position_in.section_id and position_in.section_id != position.section_id):
        section_id = position_in.section_id or position.section_id
        code = position_in.code or position.code
        existing_position = await crud.position.get_by_code_and_section(
            db, code=code, section_id=section_id
        )
        if existing_position and existing_position.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Должность с таким кодом уже существует в данном отделе",
            )
            
    # Если меняется отдел, проверяем его существование
    if position_in.section_id and position_in.section_id != position.section_id:
        section = await crud.section.get(db, id=position_in.section_id)
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отдел не найден",
            )
    
    # Сохраняем ID функций перед обновлением должности
    function_ids = position_in.function_ids
    
    # Если передан список функций, обновляем функциональные назначения
    if function_ids is not None:
        # Получаем текущие функциональные назначения
        query = select(FunctionalAssignment.function_id).where(FunctionalAssignment.position_id == id)
        result = await db.execute(query)
        current_function_ids = [function_id for function_id, in result]
        
        # Определяем, какие функции нужно добавить, а какие удалить
        functions_to_add = [f_id for f_id in function_ids if f_id not in current_function_ids]
        functions_to_remove = [f_id for f_id in current_function_ids if f_id not in function_ids]
        
        # Удаляем ненужные функциональные назначения
        if functions_to_remove:
            delete_stmt = delete(FunctionalAssignment).where(
                FunctionalAssignment.position_id == id,
                FunctionalAssignment.function_id.in_(functions_to_remove)
            )
            await db.execute(delete_stmt)
        
        # Добавляем новые функциональные назначения
        for function_id in functions_to_add:
            # Проверяем существование функции
            function = await crud.function.get(db, id=function_id)
            if not function:
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Функция с ID {function_id} не найдена",
                )
            
            # Создаем функциональное назначение
            assignment = FunctionalAssignment(
                position_id=id,
                function_id=function_id,
                is_primary=False  # По умолчанию не основная функция
            )
            db.add(assignment)
        
        await db.commit()
    
    # Обновляем должность без function_ids
    position_data = position_in.dict(exclude={"function_ids"}, exclude_unset=True)
    position = await crud.position.update(db, db_obj=position, obj_in=position_data)
    
    # Получаем обновленный список функций для ответа
    query = select(FunctionalAssignment.function_id).where(FunctionalAssignment.position_id == id)
    result = await db.execute(query)
    position.function_ids = [function_id for function_id, in result]
    
    return position

@router.delete("/{id}", response_model=Position)
async def delete_position(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить должность
    """
    position = await crud.position.get(db, id=id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Должность не найдена",
        )
    
    # Получаем ID функций перед удалением должности
    query = select(FunctionalAssignment.function_id).where(FunctionalAssignment.position_id == id)
    result = await db.execute(query)
    function_ids = [function_id for function_id, in result]
    
    # Удаление должности автоматически удалит связанные функциональные назначения благодаря внешним ключам с CASCADE
    position = await crud.position.remove(db, id=id)
    
    # Добавляем ID функций в ответ
    position.function_ids = function_ids
    
    return position 