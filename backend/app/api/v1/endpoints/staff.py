from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app import crud, models, schemas
from app.api import deps
from app.core.security import generate_activation_code # Импортируем генератор кода

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.StaffCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_staff(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    staff_in: schemas.StaffCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # TODO: Добавить проверку прав
) -> schemas.StaffCreateResponse:
    """Создание нового сотрудника.
    
    Если `create_user`=True, также создается связанный пользователь
    и возвращается объект сотрудника вместе с кодом активации.
    """
    # TODO: Добавить проверку прав доступа
    
    # Сначала создаем сотрудника
    # Используем commit=False, чтобы транзакция не завершалась сразу
    staff = await crud.staff.create(db=db, obj_in=staff_in, commit=False)
    
    response_data = staff.dict() # Преобразуем в словарь для добавления кода
    response_data["activation_code"] = None # Инициализируем

    if staff_in.create_user:
        if not staff.email:
            await db.rollback() # Откатываем создание сотрудника
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email is required to create a user for the staff member."
            )
        
        existing_user = await crud.user.get_by_email(db=db, email=staff.email)
        if existing_user:
            await db.rollback() # Откатываем создание сотрудника
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"User with email {staff.email} already exists."
            )
            
        user_in = schemas.UserCreate(
            email=staff.email, 
            full_name=staff.full_name(), 
            password=None
        )
        try:
            # commit=False, чтобы пользователь и обновление сотрудника были в одной транзакции
            new_user = await crud.user.create(db=db, obj_in=user_in, commit=False) 
            staff.user_id = new_user.id
            db.add(staff)
            # Теперь коммитим всё вместе
            await db.commit()
            await db.refresh(staff)
            await db.refresh(new_user)
            response_data["activation_code"] = new_user.activation_code
            logger.info(f"Создан пользователь для сотрудника {staff.id}. Код: {new_user.activation_code}")
        except Exception as e:
            await db.rollback() # Откатываем всю транзакцию
            logger.error(f"Ошибка создания пользователя для сотрудника {staff.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user for staff member."
            )
    else:
        # Если юзер не создается, коммитим только сотрудника
        await db.commit()
        await db.refresh(staff)
            
    # Возвращаем данные в формате StaffCreateResponse
    # Pydantic сам создаст объект из словаря
    return response_data

@router.get("/", response_model=List[schemas.Staff])
async def read_staff_list(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(deps.get_current_active_user) # TODO: Добавить проверку прав
) -> List[models.Staff]:
    """Получение списка сотрудников"""
    staff_list = await crud.staff.get_multi(db, skip=skip, limit=limit)
    return staff_list

@router.get("/{staff_id}", response_model=schemas.Staff)
async def read_staff(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    # current_user: models.User = Depends(deps.get_current_active_user) # TODO: Добавить проверку прав
) -> models.Staff:
    """Получение информации о сотруднике по ID"""
    staff = await crud.staff.get(db=db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    return staff

@router.put("/{staff_id}", response_model=schemas.Staff)
async def update_staff(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    staff_in: schemas.StaffUpdate,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # TODO: Добавить проверку прав
) -> models.Staff:
    """Обновление информации о сотруднике"""
    staff = await crud.staff.get(db=db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    
    # TODO: Добавить логику, если при обновлении меняется email и нужно обновить связанного пользователя?
    
    updated_staff = await crud.staff.update(db=db, db_obj=staff, obj_in=staff_in)
    return updated_staff

@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # TODO: Добавить проверку прав
) -> None:
    """Удаление сотрудника"""
    staff = await crud.staff.get(db=db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    
    # TODO: Что делать со связанным пользователем при удалении сотрудника?
    # Деактивировать? Удалять? Оставить?
    # Пока просто удаляем сотрудника.
    
    await crud.staff.remove(db=db, id=staff_id)
    return None 