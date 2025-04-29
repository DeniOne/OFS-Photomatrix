from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.Function)
async def create_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    function_in: schemas.FunctionCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Function:
    """Создание новой функции"""
    function = await crud.function.create(db=db, obj_in=function_in)
    return function

@router.get("/", response_model=List[schemas.Function])
async def read_functions(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> List[models.Function]:
    """Получение списка функций"""
    functions = await crud.function.get_multi(db, skip=skip, limit=limit)
    return functions

@router.get("/{function_id}", response_model=schemas.Function)
async def read_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    function_id: int,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> models.Function:
    """Получение информации о функции по ID"""
    function = await crud.function.get(db=db, id=function_id)
    if not function:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Function not found")
    return function

@router.put("/{function_id}", response_model=schemas.Function)
async def update_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    function_id: int,
    function_in: schemas.FunctionUpdate,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Function:
    """Обновление информации о функции"""
    function = await crud.function.get(db=db, id=function_id)
    if not function:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Function not found")
    updated_function = await crud.function.update(db=db, db_obj=function, obj_in=function_in)
    return updated_function

@router.delete("/{function_id}", response_model=schemas.Function)
async def delete_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    function_id: int,
    # current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.Function:
    """Удаление функции"""
    try:
        function = await crud.function.get(db=db, id=function_id)
        if not function:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Function not found")
        
        # Удаляем функцию без дополнительных проверок
        await crud.function.remove(db=db, id=function_id)
        
        logger.info(f"Функция с ID {function_id} успешно удалена")
        return function
    except Exception as e:
        logger.error(f"Ошибка при удалении функции {function_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении функции: {str(e)}"
        )

# Добавляем OPTIONS метод для CORS preflight запросов
@router.options("/{function_id}")
async def options_function(function_id: int):
    """
    CORS preflight handler для доступа к отдельной функции
    """
    return {} 