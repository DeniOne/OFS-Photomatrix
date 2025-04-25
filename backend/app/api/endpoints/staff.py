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
    
    Если указан `position_id`, создается запись в StaffPosition, связывающая сотрудника с должностью.
    """
    logger.info(f"Попытка создания сотрудника: {staff_in.email}")
    
    # Шаг 1: Подготовка данных для создания модели Staff 
    # Исключаем поля, которых нет в модели Staff
    try:
        obj_in_data = {}
        # Копируем все поля из staff_in, кроме тех, которые не входят в модель Staff
        excluded_fields = ["create_user", "position_id", "organization_id", "location_id", "is_primary_position"]
        for field, value in staff_in.dict(exclude_none=True).items():
            if field not in excluded_fields:
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
        # Проверяем, указана ли должность и организация
        has_position_data = staff_in.position_id is not None
        if has_position_data:
            # Проверяем существование должности
            position = await crud.position.get(db=db, id=staff_in.position_id)
            if not position:
                logger.error(f"Должность с ID {staff_in.position_id} не найдена")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Position with ID {staff_in.position_id} not found"
                )
        
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
                
                # Шаг 6: Если указана должность, создаем связь с должностью
                if has_position_data:
                    staff_position = models.StaffPosition(
                        staff_id=staff.id,
                        position_id=staff_in.position_id,
                        is_primary=staff_in.is_primary_position,
                        start_date=staff.hire_date
                    )
                    db.add(staff_position)
                
                # Шаг 7: Коммитим транзакцию
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
            await db.flush()
            await db.refresh(staff)
            
            # Если указана должность, создаем связь с должностью
            if has_position_data:
                staff_position = models.StaffPosition(
                    staff_id=staff.id,
                    position_id=staff_in.position_id,
                    is_primary=staff_in.is_primary_position,
                    start_date=staff.hire_date
                )
                db.add(staff_position)
            
            await db.commit()
            await db.refresh(staff)
            logger.info(f"Создан сотрудник с ID {staff.id} (без пользователя)")
            
        # Шаг 8: Формируем ответ
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

@router.post("/{staff_id}/photo", response_model=schemas.Staff)
async def upload_staff_photo(
    *,
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    photo: UploadFile = File(...),
    # current_user: models.User = Depends(deps.get_current_active_user)
):
    """Загрузить фотографию сотрудника."""
    logger.info(f"Загрузка фото для сотрудника {staff_id}")
    
    # Проверяем существование сотрудника
    staff = await crud.staff.get(db=db, id=staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found"
        )
    
    # Сохраняем фото и получаем путь
    photo_path = await save_staff_photo(photo)
    if not photo_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save photo. Invalid file format."
        )
    
    # Обновляем путь к фото у сотрудника
    updated_staff = await crud.staff.update(
        db=db,
        db_obj=staff,
        obj_in={"photo_path": photo_path}
    )
    
    return updated_staff

@router.post("/{staff_id}/document", response_model=schemas.Staff)
async def upload_staff_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    document: UploadFile = File(...),
    doc_type: str = Form(...),
    # current_user: models.User = Depends(deps.get_current_active_user)
):
    """Загрузить документ сотрудника (паспорт, договор и т.д.)."""
    logger.info(f"Загрузка документа типа '{doc_type}' для сотрудника {staff_id}")
    
    # Проверяем существование сотрудника
    staff = await crud.staff.get(db=db, id=staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found"
        )
    
    # Сохраняем документ и получаем словарь с путем
    doc_info = await save_staff_document(document, doc_type)
    if not doc_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save document. Invalid file format."
        )
    
    # Объединяем новый документ с существующими
    current_docs = staff.document_paths or {}
    current_docs.update(doc_info)
    
    # Обновляем пути к документам у сотрудника
    updated_staff = await crud.staff.update(
        db=db,
        db_obj=staff,
        obj_in={"document_paths": current_docs}
    )
    
    return updated_staff

@router.delete("/{staff_id}/document/{doc_type}", response_model=schemas.Staff)
async def delete_staff_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    doc_type: str,
    # current_user: models.User = Depends(deps.get_current_active_user)
):
    """Удалить документ сотрудника определенного типа."""
    logger.info(f"Удаление документа типа '{doc_type}' для сотрудника {staff_id}")
    
    # Проверяем существование сотрудника
    staff = await crud.staff.get(db=db, id=staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found"
        )
    
    # Проверяем наличие документа данного типа
    if not staff.document_paths or doc_type not in staff.document_paths:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document of type '{doc_type}' not found for this staff member"
        )
    
    # Удаляем документ из списка
    current_docs = dict(staff.document_paths)
    del current_docs[doc_type]
    
    # Обновляем пути к документам у сотрудника
    updated_staff = await crud.staff.update(
        db=db,
        db_obj=staff,
        obj_in={"document_paths": current_docs}
    )
    
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
    logger.info(f"Обновление сотрудника с ID {staff_id}: {staff_in}")
    
    staff = await crud.staff.get(db=db, id=staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    
    # Обработка создания пользователя при обновлении, если такой флаг установлен
    if staff_in.create_user and not staff.user_id:
        logger.info(f"Запрос на создание пользователя для сотрудника {staff_id}")
        # Проверяем, есть ли email для создания пользователя
        staff_email = staff_in.email or staff.email
        if not staff_email:
            logger.error("Email не указан при запросе создания пользователя")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email is required to create a user for the staff member."
            )
        
        # Проверяем, существует ли уже пользователь с таким email
        existing_user = await crud.user.get_by_email(db=db, email=staff_email)
        if existing_user:
            logger.warning(f"Пользователь с email {staff_email} уже существует")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"User with email {staff_email} already exists."
            )
            
        try:
            # Создаем пользователя
            user_in = schemas.UserCreate(
                email=staff_email, 
                full_name=f"{staff.last_name} {staff.first_name} {staff.middle_name if staff.middle_name else ''}", 
                password=None
            )
            
            # Создаем пользователя
            new_user = await crud.user.create(db=db, obj_in=user_in, commit=False)
            
            # Связываем сотрудника с пользователем
            staff_in_dict = staff_in.dict(exclude_none=True)
            staff_in_dict["user_id"] = new_user.id
            
            # Обновляем словарь для обновления сотрудника
            staff_in = schemas.StaffUpdate(**staff_in_dict)
            
            # Коммитим транзакцию
            await db.commit()
            await db.refresh(new_user)
            
            logger.info(f"Пользователь создан и связан с сотрудником. ID пользователя: {new_user.id}")
            
            # Возвращаем код активации в ответе
            # Т.к. в схеме Staff нет поля activation_code, нужно его передать другим способом
            # Можно использовать заголовки ответа, но проще всего отобразить его в UI через notifications
            activation_code = new_user.activation_code
            logger.info(f"Код активации: {activation_code}")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Ошибка при создании пользователя: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
    
    # Обновляем сотрудника
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