from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
import logging
import json
from fastapi.encoders import jsonable_encoder
from datetime import datetime  # Добавляем импорт datetime

from app import crud, models, schemas
from app.api import deps
from app.core.file_utils import save_staff_photo, save_staff_document

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
    logger.info(f"Попытка создания сотрудника: {staff_in.email}")
    
    # Шаг 1: Подготовка данных для создания модели Staff 
    # Исключаем поле create_user, которого нет в модели Staff
    try:
        obj_in_data = {}
        # Копируем все поля из staff_in, кроме create_user
        for field, value in staff_in.dict(exclude_none=True).items():
            if field != "create_user":
                # Если поле - hire_date, преобразуем его из строки в объект date
                if field == "hire_date" and value and isinstance(value, str):
                    try:
                        # Пробуем парсить дату в формате ДД.ММ.ГГГГ
                        if "." in value:
                            day, month, year = value.split(".")
                            value = datetime.date(int(year), int(month), int(day))
                        # Пробуем парсить дату в формате ГГГГ-ММ-ДД
                        elif "-" in value:
                            year, month, day = value.split("-")
                            value = datetime.date(int(year), int(month), int(day))
                        logger.info(f"Дата преобразована: {value}")
                    except Exception as e:
                        logger.error(f"Ошибка при парсинге даты '{value}': {e}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid date format: {value}. Expected DD.MM.YYYY or YYYY-MM-DD."
                        )
                obj_in_data[field] = value
                
        logger.debug(f"Подготовленные данные: {obj_in_data}")
    except Exception as e:
        logger.error(f"Ошибка при подготовке данных: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data preparation error: {str(e)}"
        )
    
    # Шаг 2: Проверка и создание сотрудника и пользователя
    response_data = {"activation_code": None}
    
    try:
        if staff_in.create_user:
            # Проверяем, есть ли email для создания пользователя
            if not staff_in.email:
                logger.error("Email не указан при запросе создания пользователя")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Email is required to create a user for the staff member."
                )
            
            # Проверяем, существует ли уже пользователь с таким email
            existing_user = await crud.user.get_by_email(db=db, email=staff_in.email)
            if existing_user:
                logger.warning(f"Пользователь с email {staff_in.email} уже существует")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"User with email {staff_in.email} already exists."
                )
                
            # Шаг 3: Создаем сотрудника
            staff = models.Staff(**obj_in_data)
            db.add(staff)
            await db.flush()  # Получаем ID без коммита транзакции
            await db.refresh(staff)
            logger.info(f"Создан сотрудник с ID {staff.id} (транзакция не закоммичена)")
            
            # Шаг 4: Создаем пользователя
            user_in = schemas.UserCreate(
                email=staff_in.email, 
                full_name=staff.full_name(), 
                password=None
            )
            try:
                # Создаем пользователя без коммита
                new_user = await crud.user.create(db=db, obj_in=user_in, commit=False)
                
                # Шаг 5: Связываем сотрудника с пользователем
                staff.user_id = new_user.id
                db.add(staff)
                
                # Шаг 6: Коммитим транзакцию
                await db.commit()
                await db.refresh(staff)
                await db.refresh(new_user)
                logger.info(f"Пользователь создан и связан с сотрудником. ID пользователя: {new_user.id}")
                
                # Добавляем код активации в ответ
                response_data["activation_code"] = new_user.activation_code
            except Exception as e:
                await db.rollback()
                logger.error(f"Ошибка при создании пользователя: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create user: {str(e)}"
                )
        else:
            # Создаем только сотрудника
            staff = models.Staff(**obj_in_data)
            db.add(staff)
            await db.commit()
            await db.refresh(staff)
            logger.info(f"Создан сотрудник с ID {staff.id} (без пользователя)")
            
        # Шаг 7: Формируем ответ
        staff_dict = {column.name: getattr(staff, column.name) 
                     for column in staff.__table__.columns}
        response_data.update(staff_dict)
        
        logger.info(f"Сотрудник успешно создан. ID: {staff.id}")
        return schemas.StaffCreateResponse(**response_data)
        
    except HTTPException:
        # Пробрасываем HTTP исключения дальше
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Неожиданная ошибка при создании сотрудника: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create staff member: {str(e)}"
        )

@router.post("/upload-photo/{staff_id}", response_model=schemas.Staff)
async def upload_staff_photo(
    *,
    staff_id: int,
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(deps.get_db),
    # current_user: models.User = Depends(deps.get_current_active_user) # TODO: Добавить проверку прав
) -> models.Staff:
    """Загрузка фотографии сотрудника"""
    staff = await crud.staff.get(db=db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    
    # Сохраняем фото
    photo_path = await save_staff_photo(photo)
    if not photo_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid photo file"
        )
    
    # Удаляем старое фото, если есть
    if staff.photo_path:
        # Можно добавить функцию удаления старого файла
        pass
    
    # Обновляем путь к фото в БД
    update_data = {"photo_path": photo_path}
    updated_staff = await crud.staff.update(db=db, db_obj=staff, obj_in=update_data)
    
    return updated_staff

@router.post("/upload-document/{staff_id}", response_model=schemas.Staff)
async def upload_staff_document(
    *,
    staff_id: int,
    document: UploadFile = File(...),
    document_type: str = Form(...),
    db: AsyncSession = Depends(deps.get_db),
    # current_user: models.User = Depends(deps.get_current_active_user) # TODO: Добавить проверку прав
) -> models.Staff:
    """Загрузка документа сотрудника.
    
    document_type - тип документа (например, "passport", "contract", "resume")
    """
    staff = await crud.staff.get(db=db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    
    # Сохраняем документ
    doc_info = await save_staff_document(document, document_type)
    if not doc_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document file"
        )
    
    # Обновляем документы в БД
    current_docs = staff.document_paths or {}
    current_docs.update(doc_info)
    
    update_data = {"document_paths": current_docs}
    updated_staff = await crud.staff.update(db=db, db_obj=staff, obj_in=update_data)
    
    return updated_staff

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