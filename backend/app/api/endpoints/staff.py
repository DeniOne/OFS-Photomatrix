from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
import json
from fastapi.encoders import jsonable_encoder
from datetime import datetime  # Добавляем импорт datetime
from sqlalchemy import select, update, delete

from app import crud, models, schemas
from app.api import deps
from app.core.file_utils import save_staff_photo, save_staff_document

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.StaffCreateResponse)
async def create_staff(
    *,
    db: AsyncSession = Depends(deps.get_db),
    staff_in: schemas.StaffCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # TODO: Добавить проверку прав
) -> Any:
    """Создание нового сотрудника"""
    try:
        logger.info(f"Запрос на создание сотрудника: {staff_in.dict(exclude_none=True)}")
        # Проверка существования организации
        organization_id = staff_in.organization_id
        if organization_id:
            org_query = select(models.Organization).filter(models.Organization.id == organization_id)
            org_result = await db.execute(org_query)
            organization = org_result.scalars().first()
            
            if not organization:
                logger.error(f"Организация с ID {organization_id} не найдена")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Organization with ID {organization_id} not found"
                )
                
            logger.info(f"Организация найдена: {organization.name}")
        
        # Создаем сотрудника в БД
        staff_in_data = staff_in.dict(exclude={"positions", "create_user", "password"})
        staff = models.Staff(**staff_in_data)
        db.add(staff)
        
        # Выполняем flush для получения ID сотрудника
        await db.flush()
        await db.refresh(staff)
        
        # Обработка позиций если они указаны
        if staff_in.positions and len(staff_in.positions) > 0:
            # Для каждой должности в запросе
            for position_data in staff_in.positions:
                # Проверяем существование должности
                position = await crud.position.get(db=db, id=position_data.position_id)
                if not position:
                    await db.rollback()
                    logger.error(f"Должность с ID {position_data.position_id} не найдена")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Position with ID {position_data.position_id} not found"
                    )
                
                # Создаем связь staff_position
                staff_position = models.StaffPosition(
                    staff_id=staff.id,
                    position_id=position_data.position_id,
                    is_primary=position_data.is_primary,
                    start_date=staff.hire_date
                )
                db.add(staff_position)
                logger.info(f"Добавлена должность {position.name} для сотрудника")
        
        # Обработка создания пользователя, если запрошено
        activation_code = None
        if staff_in.create_user:
            logger.info("Запрос на создание пользователя вместе с сотрудником")
            if not staff.email:
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Email is required to create a user for the staff member."
                )
                
            # Проверяем, что пользователя с таким email еще нет
            existing_user = await crud.user.get_by_email(db=db, email=staff.email)
            if existing_user:
                await db.rollback()
                logger.warning(f"Пользователь с email {staff.email} уже существует")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"User with email {staff.email} already exists."
                )
                
            # Создаем пользователя
            user_in = schemas.UserCreate(
                email=staff.email, 
                full_name=f"{staff.last_name} {staff.first_name} {staff.middle_name if staff.middle_name else ''}",
                password=staff_in.password
            )
            
            user = await crud.user.create(db=db, obj_in=user_in, commit=False)
            activation_code = user.activation_code
            
            # Связываем сотрудника с пользователем
            staff.user_id = user.id
            db.add(staff)
            
            logger.info(f"Создан пользователь с ID {user.id} и связан с сотрудником")
        
        # Коммитим транзакцию
        await db.commit()
        await db.refresh(staff)
        
        # Создаем результат для возврата
        response_dict = {
            "id": staff.id,
            "first_name": staff.first_name,
            "last_name": staff.last_name,
            "middle_name": staff.middle_name,
            "email": staff.email,
            "phone": staff.phone,
            "hire_date": staff.hire_date,
            "photo_path": staff.photo_path,
            "document_paths": staff.document_paths,
            "is_active": staff.is_active,
            "user_id": staff.user_id,
            "organization_id": staff.organization_id,
            "created_at": staff.created_at,
            "updated_at": staff.updated_at,
            "activation_code": activation_code,
            "organization_name": None,
            "positions": []
        }
        
        # Добавляем название организации, если есть
        if staff.organization_id:
            org_query = select(models.Organization).filter(models.Organization.id == staff.organization_id)
            org_result = await db.execute(org_query)
            organization = org_result.scalars().first()
            if organization:
                response_dict["organization_name"] = organization.name
        
        # Загружаем информацию о должностях
        sp_query = select(models.StaffPosition).filter(models.StaffPosition.staff_id == staff.id)
        sp_result = await db.execute(sp_query)
        staff_positions = sp_result.scalars().all()
        
        positions_list = []
        for sp in staff_positions:
            position_data = {
                "id": sp.id,
                "staff_id": sp.staff_id,
                "position_id": sp.position_id,
                "is_primary": sp.is_primary,
                "position_name": None
            }
            
            # Получаем информацию о должности
            pos_query = select(models.Position).filter(models.Position.id == sp.position_id)
            pos_result = await db.execute(pos_query)
            position = pos_result.scalars().first()
            
            if position:
                position_data["position_name"] = position.name
            
            positions_list.append(position_data)
        
        response_dict["positions"] = positions_list
        
        logger.info(f"Сотрудник успешно создан, ID: {staff.id}")
        return schemas.StaffCreateResponse(**response_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании сотрудника: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create staff: {str(e)[:100]}"
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
async def get_staffs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Получить список сотрудников.
    """
    try:
        staffs = await crud.staff.get_multi(db, skip=skip, limit=limit)
        # Добавляем объекты обратно в сессию, чтобы избежать ошибок с отсоединенными объектами
        for staff in staffs:
            db.add(staff)
            
        # Расширенная диагностика для отладки
        print(f"Retrieved {len(staffs)} staff records")
        
        # Заменяем лениво загружаемые отношения простыми объектами
        result = []
        for staff in staffs:
            staff_dict = {
                "id": staff.id,
                "first_name": staff.first_name,
                "last_name": staff.last_name,
                "email": staff.email,
                "phone": staff.phone,
                "hire_date": staff.hire_date,
                "photo_path": staff.photo_path,
                "is_active": staff.is_active,
                "created_at": staff.created_at,
                "updated_at": staff.updated_at,
                # Безопасный доступ к связанным объектам
                "division_id": getattr(staff, "division_id", None),
                "position_id": getattr(staff, "position_id", None)
            }
            
            # Добавляем простые версии связанных объектов, если они есть
            if hasattr(staff, "division") and staff.division is not None:
                staff_dict["division"] = {"id": staff.division.id, "name": staff.division.name}
            else:
                staff_dict["division"] = None
                
            if hasattr(staff, "position") and staff.position is not None:
                staff_dict["position"] = {"id": staff.position.id, "name": staff.position.name}
            else:
                staff_dict["position"] = None
                
            result.append(schemas.Staff(**staff_dict))
            
        return result
    except Exception as e:
        print(f"Error in get_staffs: {str(e)}")
        # В случае ошибки возвращаем пустой список
        return []

@router.get("/{staff_id}", response_model=schemas.Staff)
async def read_staff(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Получение информации о сотруднике по ID"""
    try:
        # Получаем сотрудника без ленивой загрузки
        query = select(models.Staff).filter(models.Staff.id == staff_id)
        result = await db.execute(query)
        staff = result.scalars().first()
        
        if not staff:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
            
        # Создаем базовый словарь с полями из таблицы staff
        staff_dict = {
            "id": staff.id,
            "first_name": staff.first_name,
            "last_name": staff.last_name,
            "middle_name": staff.middle_name,
            "email": staff.email,
            "phone": staff.phone,
            "hire_date": staff.hire_date,
            "photo_path": staff.photo_path,
            "document_paths": staff.document_paths,
            "is_active": staff.is_active,
            "user_id": staff.user_id,
            "organization_id": staff.organization_id, # Добавим organization_id
            "created_at": staff.created_at,
            "updated_at": staff.updated_at,
            "organization_name": None, # Начнем с None
            "positions": [], # Инициализируем список должностей
            "user": None # Инициализируем пользователя
        }
        
        # 1. Получаем организацию напрямую, если есть organization_id
        if staff.organization_id:
            org_query = select(models.Organization).filter(models.Organization.id == staff.organization_id)
            org_result = await db.execute(org_query)
            organization = org_result.scalars().first()
            if organization:
                staff_dict["organization_name"] = organization.name
        
        # 2. Получаем назначения должностей и пытаемся определить организацию через основную должность, если она не найдена напрямую
        sp_query = select(models.StaffPosition).filter(models.StaffPosition.staff_id == staff_id)
        sp_result = await db.execute(sp_query)
        staff_positions = sp_result.scalars().all()
        
        positions_list = []
        primary_position_found = False
        
        for sp in staff_positions:
            position_name = None
            # Получаем информацию о должности через отдельный запрос
            pos_query = select(models.Position).filter(models.Position.id == sp.position_id)
            pos_result = await db.execute(pos_query)
            position = pos_result.scalars().first()
            
            if position:
                position_name = position.name
                # Пытаемся определить организацию через основную должность, если она еще не найдена
                if not staff_dict["organization_name"] and sp.is_primary and position.section_id:
                    primary_position_found = True # Отметим, что нашли основную должность
                    # ... (остальная цепочка запросов section -> division -> organization)
                    section_query = select(models.Section).filter(models.Section.id == position.section_id)
                    section_result = await db.execute(section_query)
                    section = section_result.scalars().first()
                    
                    if section and section.division_id:
                        division_query = select(models.Division).filter(models.Division.id == section.division_id)
                        division_result = await db.execute(division_query)
                        division = division_result.scalars().first()
                        
                        if division and division.organization_id:
                            org_query_nested = select(models.Organization).filter(models.Organization.id == division.organization_id)
                            org_result_nested = await db.execute(org_query_nested)
                            organization_nested = org_result_nested.scalars().first()
                            
                            if organization_nested:
                                staff_dict["organization_name"] = organization_nested.name

            # Формируем словарь для схемы StaffPosition
            sp_dict = {
                "id": sp.id,
                "staff_id": sp.staff_id,
                "position_id": sp.position_id,
                "is_primary": sp.is_primary,
                "position_name": position_name 
            }
            positions_list.append(sp_dict)
            
        # Если организация так и не найдена, ставим заглушку
        if not staff_dict["organization_name"]:
             staff_dict["organization_name"] = "Не указана"

        # Добавляем сформированный список должностей
        staff_dict["positions"] = positions_list
        
        # 3. Получаем пользователя, если он есть
        if staff.user_id:
            user_query = select(models.User).filter(models.User.id == staff.user_id)
            user_result = await db.execute(user_query)
            user = user_result.scalars().first()
            
            if user:
                # Формируем словарь для схемы User (убедись, что она есть в schemas.staff)
                staff_dict["user"] = {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_active": user.is_active
                    # Добавь другие поля из схемы User, если нужно
                }

        logger.info(f"Успешно получен сотрудник с должностями, ID: {staff.id}")
        # Возвращаем данные, соответствующие схеме Staff
        return schemas.Staff(**staff_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"Error in read_staff: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve staff: {error_msg[:100]}"
        )

@router.put("/{staff_id}", response_model=schemas.Staff)
async def update_staff(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    staff_id: int,
    staff_in: schemas.StaffUpdate,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # TODO: Добавить проверку прав
) -> Any:
    """Обновление информации о сотруднике"""
    logger.info(f"Обновление сотрудника с ID {staff_id}. Данные: {staff_in.dict(exclude_none=True)}")
    
    try:
        # Получаем сотрудника напрямую через SQL без ленивой загрузки
        query = select(models.Staff).filter(models.Staff.id == staff_id)
        result = await db.execute(query)
        staff = result.scalars().first()
        
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
                    password=staff_in.password
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
                
        # Сохранение данных об организации напрямую в поле organization_id модели Staff
        organization_id = staff_in.organization_id
        if organization_id is not None:
            # Проверяем существование организации
            logger.info(f"Проверка организации ID: {organization_id}")
            org_query = select(models.Organization).filter(models.Organization.id == organization_id)
            org_result = await db.execute(org_query)
            organization = org_result.scalars().first()
            
            if not organization:
                logger.error(f"Организация с ID {organization_id} не найдена")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Organization with ID {organization_id} not found"
                )
            
            logger.info(f"Организация найдена: {organization.name}")
            # Обновляем organization_id у сотрудника
            staff.organization_id = organization_id
            
            # Проверяем/обновляем запись в staff_organization (связующая таблица)
            so_query = select(models.StaffOrganization).filter(
                models.StaffOrganization.staff_id == staff_id,
                models.StaffOrganization.organization_id == organization_id
            )
            so_result = await db.execute(so_query)
            existing_staff_org = so_result.scalars().first()
            
            if not existing_staff_org:
                # Удаляем старые связи staff_organization для этого сотрудника (если они были)
                # Это нужно, если сотрудник может быть только в одной организации одновременно
                # Если сотрудник может быть в нескольких - эту строку нужно убрать
                delete_old_so_stmt = delete(models.StaffOrganization).where(models.StaffOrganization.staff_id == staff_id)
                await db.execute(delete_old_so_stmt)
                
                # Создаем новую связь с организацией
                staff_org = models.StaffOrganization(
                    staff_id=staff.id,
                    organization_id=organization_id,
                    is_primary=True # Устанавливаем как основную
                )
                db.add(staff_org)
                logger.info(f"Создана/обновлена связь с организацией: {organization.name}")
        elif organization_id is None and staff_in.organization_id is not None: # Если пришел null/None для organization_id
             # Если нужно разрешить отвязку от организации
             staff.organization_id = None
             # Удаляем связь из staff_organization
             delete_so_stmt = delete(models.StaffOrganization).where(models.StaffOrganization.staff_id == staff_id)
             await db.execute(delete_so_stmt)
             logger.info(f"Сотрудник отвязан от организации.")

                
        # Проверка и обработка должностей
        if staff_in.positions is not None: # Обрабатываем, даже если пришел пустой список []
            incoming_position_ids = {pos.position_id for pos in staff_in.positions}
            primary_incoming_position_id = next((pos.position_id for pos in staff_in.positions if pos.is_primary), None)
            
            # Получаем текущие назначения должностей
            current_sp_query = select(models.StaffPosition).filter(models.StaffPosition.staff_id == staff_id)
            current_sp_result = await db.execute(current_sp_query)
            current_staff_positions = current_sp_result.scalars().all()
            current_position_map = {sp.position_id: sp for sp in current_staff_positions}
            current_position_ids = set(current_position_map.keys())
            
            # Удаляем должности, которых нет во входящем списке
            ids_to_delete = current_position_ids - incoming_position_ids
            if ids_to_delete:
                delete_stmt = delete(models.StaffPosition).where(
                    models.StaffPosition.staff_id == staff_id,
                    models.StaffPosition.position_id.in_(ids_to_delete)
                )
                await db.execute(delete_stmt)
                logger.info(f"Удалены старые назначения должностей: {ids_to_delete}")

            # Добавляем/Обновляем должности из входящего списка
            for position_data in staff_in.positions:
                position_id = position_data.position_id
                is_primary = position_data.is_primary
                
                # Проверяем существование самой должности
                position = await crud.position.get(db=db, id=position_id)
                if not position:
                    logger.error(f"Должность с ID {position_id} не найдена при обновлении")
                    # Возможно, стоит откатить транзакцию или пропустить эту должность
                    continue # Пропускаем эту должность
                    # raise HTTPException(...) 

                existing_staff_position = current_position_map.get(position_id)

                if not existing_staff_position:
                    # Добавляем новую связь
                    # Если эта должность должна быть основной, сбросим флаг у других
                    if is_primary:
                        update_primary_stmt = update(models.StaffPosition).where(
                            models.StaffPosition.staff_id == staff_id,
                            models.StaffPosition.is_primary == True
                        ).values(is_primary=False)
                        await db.execute(update_primary_stmt)
                        
                    new_sp = models.StaffPosition(
                        staff_id=staff.id,
                        position_id=position_id,
                        is_primary=is_primary,
                        start_date=staff.hire_date # Или брать из position_data, если там есть?
                    )
                    db.add(new_sp)
                    logger.info(f"Добавлено новое назначение должности: {position.name}")
                elif existing_staff_position.is_primary != is_primary:
                    # Обновляем флаг is_primary, если он изменился
                    # Если эта должность СТАЛА основной
                    if is_primary:
                         # Сбросим флаг у других
                        update_primary_stmt = update(models.StaffPosition).where(
                            models.StaffPosition.staff_id == staff_id,
                            models.StaffPosition.is_primary == True,
                            models.StaffPosition.position_id != position_id # Кроме текущей
                        ).values(is_primary=False)
                        await db.execute(update_primary_stmt)
                    
                    existing_staff_position.is_primary = is_primary
                    db.add(existing_staff_position)
                    logger.info(f"Обновлен флаг is_primary для должности: {position.name}")
        
        # Исключаем поля, которые обрабатываются отдельно
        staff_update_data = staff_in.dict(
            exclude={"positions", "create_user", "password", "organization_id"}, # Исключаем organization_id т.к. обновили выше
            exclude_unset=True,
            exclude_none=True
        )
        
        # Обновляем остальные поля сотрудника
        for field, value in staff_update_data.items():
            setattr(staff, field, value) 
        
        db.add(staff) # Добавляем обновленный staff и новые/измененные StaffPosition/StaffOrganization в сессию
        await db.commit()
        await db.refresh(staff) # Обновляем объект staff из БД
        
        # Получаем обновленную информацию о сотруднике для ответа (используем read_staff или похожую логику)
        # Используем существующую логику read_staff, чтобы ответ был консистентным
        return await read_staff(db=db, staff_id=staff_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении сотрудника: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update staff: {str(e)[:100]}"
        )

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