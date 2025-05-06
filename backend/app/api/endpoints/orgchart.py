from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
import logging

from app import models, schemas
from app.api import deps
from app.models.division import DivisionType

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=Dict[str, Any])
async def get_org_chart(
    db: AsyncSession = Depends(deps.get_db),
    org_id: Optional[int] = None,
    # current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Получение полной бизнес-структуры в виде дерева для построения диаграммы.
    
    Включает:
    - Совет Учредителей
    - Руководство (Гендиректор, Директора)
    - Департаменты
    - Отделы
    - Функции
    - Должности с сотрудниками
    """
    logger.info(f"Запрос на получение бизнес-структуры. org_id={org_id}")
    
    try:
        # Создаем узел Совета Учредителей как корень бизнес-структуры
        board = {
            "id": "board-1",
            "name": "Совет Учредителей",
            "type": "board",
            "children": []
        }
        
        # Создаем бизнес-структуру с Советом Учредителей на вершине
        business_structure = [board]
        
        # 1. Получаем все позиции, чтобы найти руководство
        positions_query = select(models.Position).options(
            selectinload(models.Position.staff_positions).selectinload(models.StaffPosition.staff)
        )
        positions_result = await db.execute(positions_query)
        all_positions = positions_result.scalars().all()
        
        # Найдем руководящие позиции по атрибуту и имени
        ceo_position = None  # Генеральный директор
        directors = []       # Остальные директора
        
        for position in all_positions:
            # Пропускаем неактивные позиции
            if hasattr(position, 'is_active') and not position.is_active:
                continue
                
            # Флаги, определяющие тип позиции
            is_top = False    # Это топ-менеджер?
            is_ceo = False    # Это ген.директор?
            
            # Проверяем атрибуты и имя позиции
            if position.attribute:
                attr_lower = position.attribute.lower() if position.attribute else ""
                # Любые руководящие должности
                if any(term in attr_lower for term in ["директор", "руководи", "менеджмент", "head", "chief"]):
                    is_top = True
                # Генеральный директор
                if any(term in attr_lower for term in ["генеральный", "general", "ceo", "главный"]):
                    is_top = True
                    is_ceo = True
            
            # Также проверяем по имени должности
            if position.name:
                name_lower = position.name.lower() if position.name else ""
                if "директор" in name_lower:
                    is_top = True
                    # Если это генеральный директор
                    if any(term in name_lower for term in ["генеральный", "главный", "general", "ceo"]):
                        is_ceo = True
                # Другие варианты руководящих должностей
                elif any(term in name_lower for term in ["руководитель", "начальник", "head", "chief"]):
                    is_top = True
            
            # Если определили как руководящую позицию
            if is_top:
                # Создаем узел для позиции
                position_node = await build_position_node(db, position)
                
                # Присваиваем уровень для отображения
                position_node["position_level"] = 1
                
                # Если это генеральный директор
                if is_ceo and not ceo_position:
                    ceo_position = position
                    board["children"].append(position_node)  # Добавляем под Совет Учредителей
                else:
                    directors.append((position, position_node))  # Сохраняем для добавления позже
        
        # Если не нашли генерального директора, но есть другие директора
        if not ceo_position and directors:
            # Берем первого директора как условного главного
            first_position, first_node = directors.pop(0)
            board["children"].append(first_node)
            ceo_position = first_position
        
        # Только если есть генеральный директор
        if ceo_position:
            # Получаем ссылку на узел с генеральным директором
            ceo_node = board["children"][0] if board["children"] else None
            
            # Если есть узел гендиректора и другие директора
            if ceo_node and directors:
                # Убедимся, что у генерального директора есть свойство children
                if "children" not in ceo_node:
                    ceo_node["children"] = []
                
                # Добавляем остальных директоров как подчиненных гендиректору
                for _, director_node in directors:
                    ceo_node["children"].append(director_node)
            
            # 2. Получаем департаменты, чтобы связать их с директорами
            divisions_query = select(models.Division).options(
                selectinload(models.Division.positions),
                selectinload(models.Division.sections).selectinload(models.Section.positions)
            )
            divisions_result = await db.execute(divisions_query)
            all_divisions = divisions_result.scalars().all()
            
            # Только активные и корневые департаменты
            root_departments = [div for div in all_divisions if 
                               (not hasattr(div, 'is_active') or div.is_active) and 
                               (not div.parent_id) and
                               (hasattr(div, 'type') and div.type == DivisionType.DEPARTMENT)]
            
            # Для каждого директора ищем соответствующие департаменты
            if ceo_node and "children" in ceo_node:
                # Для гендиректора - ему не привязываем департаменты напрямую
                
                # Для каждого директора под гендиректором
                for i, (director_position, director_node) in enumerate(directors):
                    # Убедимся, что у директора есть свойство children
                    if "children" not in director_node:
                        director_node["children"] = []
                    
                    # По имени директора определяем, какие департаменты к нему относятся
                    director_name = director_position.name.lower() if director_position.name else ""
                    
                    # Набор департаментов для этого директора
                    matching_departments = []
                    
                    # Ищем департаменты, соответствующие директору по названию
                    for dept in root_departments:
                        # Инициализируем флаг соответствия
                        is_matching = False
                        
                        # Если у департамента есть название
                        if dept.name:
                            dept_name = dept.name.lower()
                            
                            # Если это финансовый директор
                            if any(term in director_name for term in ["финанс", "finance", "cfo", "финдир"]):
                                if any(term in dept_name for term in ["финанс", "finance", "бухгалт", "accounting"]):
                                    is_matching = True
                            
                            # Если это технический директор или CTO
                            elif any(term in director_name for term in ["технич", "technical", "cto", "технол"]):
                                if any(term in dept_name for term in ["разраб", "technical", "it", "ит", "технол", "произв"]):
                                    is_matching = True
                            
                            # Если это коммерческий директор
                            elif any(term in director_name for term in ["коммерч", "commercial", "sales", "продаж"]):
                                if any(term in dept_name for term in ["продаж", "sales", "коммерч", "commercial", "маркет", "market"]):
                                    is_matching = True
                            
                            # Если это директор по персоналу
                            elif any(term in director_name for term in ["персонал", "hr", "кадр"]):
                                if any(term in dept_name for term in ["персонал", "hr", "кадр"]):
                                    is_matching = True
                            
                            # Если это операционный директор
                            elif any(term in director_name for term in ["операци", "operation"]):
                                if any(term in dept_name for term in ["операци", "operation", "логист", "logist"]):
                                    is_matching = True
                            
                            # Если не смогли определить, но это последний директор, и еще есть непривязанные департаменты
                            elif i == len(directors) - 1 and len(matching_departments) == 0:
                                # Добавим оставшиеся департаменты к последнему директору
                                is_matching = True
                        
                        # Если нашли соответствие
                        if is_matching:
                            matching_departments.append(dept)
                            
                    # Для каждого соответствующего департамента
                    for dept in matching_departments:
                        # Создаем узел департамента
                        dept_node = {
                            "id": f"div-{dept.id}",
                            "name": dept.name,
                            "type": "division",
                            "children": []
                        }
                        
                        # Добавляем отделы (секции) департамента
                        if hasattr(dept, 'sections') and dept.sections:
                            for section in dept.sections:
                                # Создаем узел отдела
                                section_node = {
                                    "id": f"sec-{section.id}",
                                    "name": section.name,
                                    "type": "section",
                                    "children": []
                                }
                                
                                # Добавляем должности отдела
                                if hasattr(section, 'positions') and section.positions:
                                    for position in section.positions:
                                        position_node = await build_position_node(db, position)
                                        section_node["children"].append(position_node)
                                
                                # Добавляем отдел к департаменту, если в нем есть должности
                                if section_node["children"]:
                                    dept_node["children"].append(section_node)
                        
                        # Добавляем должности департамента (не привязанные к отделам)
                        if hasattr(dept, 'positions') and dept.positions:
                            for position in dept.positions:
                                position_node = await build_position_node(db, position)
                                dept_node["children"].append(position_node)
                        
                        # Добавляем департамент к директору
                        director_node["children"].append(dept_node)
        
        # 3. Если не нашли ни одного директора или структура пустая
        if not board["children"]:
            # Резервный вариант - используем организации напрямую
            logger.warning("Не найдено ни одной руководящей позиции, использую обычную структуру организаций")
            
            # Загружаем стандартную структуру организаций
            org_query = select(models.Organization).options(
                selectinload(models.Organization.divisions)
            ).where(models.Organization.parent_id == None)
            
            org_result = await db.execute(org_query)
            organizations = org_result.scalars().all()
            
            tree_nodes = []
            for org in organizations:
                org_node = await build_organization_node(db, org)
                tree_nodes.append(org_node)
            
            # Заменяем пустую бизнес-структуру на организации
            business_structure = tree_nodes
        
        # Если запрошена конкретная организация, находим её в структуре
        if org_id:
            # Ищем организацию в структуре
            org_node = None
            
            # TODO: Тут мы могли бы искать организацию в уже построенной структуре,
            # но пока просто возвращаем 404, если запрашивается конкретная организация
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Организация с ID {org_id} не найдена в бизнес-структуре"
            )
        
        # Возвращаем корневую ноду с бизнес-структурой
        return {
            "id": "root",
            "name": "Бизнес-структура",
            "title": "Корпоративная бизнес-структура",
            "type": "department",
            "children": business_structure
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении бизнес-структуры: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@router.get("/legal", response_model=Dict[str, Any])
async def get_legal_org_chart(
    db: AsyncSession = Depends(deps.get_db),
    legal_entity_id: Optional[int] = None,
    # current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Получение организационной структуры по юридическим лицам.
    
    Отображает структуру подчинения сотрудников юридическим лицам.
    """
    logger.info(f"Запрос на получение юридической структуры. legal_entity_id={legal_entity_id}")
    
    try:
        # Временная заглушка с тестовыми данными
        # TODO: Реализовать полноценную загрузку из БД
        
        legal_entities = [
            {
                "id": "org-1",
                "name": "ООО 'Фотоматрица'",
                "type": "department",
                "org_type": "LEGAL_ENTITY",
                "children": [
                    {
                        "id": "pos-101",
                        "name": "Генеральный директор",
                        "type": "position",
                        "staffName": "Иванов И.И.",
                        "staffId": "1",
                        "is_vacant": False
                    },
                    {
                        "id": "pos-102",
                        "name": "Финансовый директор",
                        "type": "position",
                        "staffName": "Петров П.П.",
                        "staffId": "2",
                        "is_vacant": False
                    },
                    {
                        "id": "pos-103",
                        "name": "Руководитель отдела кадров",
                        "type": "position",
                        "staffId": "3",
                        "staffName": "Сидорова А.В.",
                        "is_vacant": False
                    }
                ]
            },
            {
                "id": "org-2",
                "name": "ИП 'Петров'",
                "type": "department",
                "org_type": "LEGAL_ENTITY",
                "children": [
                    {
                        "id": "pos-201",
                        "name": "Индивидуальный предприниматель",
                        "type": "position",
                        "staffName": "Петров В.Г.",
                        "staffId": "4",
                        "is_vacant": False
                    },
                    {
                        "id": "pos-202",
                        "name": "Бухгалтер",
                        "type": "position",
                        "staffName": "Семенова О.Н.",
                        "staffId": "5",
                        "is_vacant": False
                    }
                ]
            }
        ]
        
        # Если запрошено конкретное юрлицо
        if legal_entity_id:
            for entity in legal_entities:
                if entity["id"] == f"org-{legal_entity_id}":
                    return entity
            
            # Если не нашли, возвращаем 404
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Юридическое лицо с ID {legal_entity_id} не найдено"
            )
        
        # Иначе возвращаем корневую ноду с юрлицами
        return {
            "id": "root",
            "name": "Юридическая структура",
            "title": "Структура по юридическим лицам",
            "type": "department",
            "children": legal_entities
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении юридической структуры: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@router.get("/location", response_model=Dict[str, Any])
async def get_location_org_chart(
    db: AsyncSession = Depends(deps.get_db),
    location_id: Optional[int] = None,
    # current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Получение организационной структуры по локациям (территориям).
    
    Отображает структуру сотрудников по географическим локациям.
    """
    logger.info(f"Запрос на получение территориальной структуры. location_id={location_id}")
    
    try:
        # Временная заглушка с тестовыми данными
        # TODO: Реализовать полноценную загрузку из БД
        
        locations = [
            {
                "id": "org-3",
                "name": "Офис Москва",
                "type": "department",
                "org_type": "LOCATION",
                "children": [
                    {
                        "id": "div-1",
                        "name": "Департамент фотосъемки",
                        "type": "division",
                        "children": [
                            {
                                "id": "sec-1",
                                "name": "Отдел студийной съемки",
                                "type": "section",
                                "children": [
                                    {
                                        "id": "pos-301",
                                        "name": "Фотограф",
                                        "type": "position",
                                        "staffName": "Сергеев И.К.",
                                        "staffId": "6",
                                        "is_vacant": False
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "div-2",
                        "name": "Департамент постобработки",
                        "type": "division",
                        "children": [
                            {
                                "id": "pos-302",
                                "name": "Дизайнер",
                                "type": "position",
                                "staffName": "Миронова К.Е.",
                                "staffId": "7",
                                "is_vacant": False
                            }
                        ]
                    }
                ]
            },
            {
                "id": "org-4",
                "name": "Офис Санкт-Петербург",
                "type": "department",
                "org_type": "LOCATION",
                "children": [
                    {
                        "id": "div-3",
                        "name": "Отдел продаж",
                        "type": "division",
                        "children": [
                            {
                                "id": "pos-401",
                                "name": "Менеджер по продажам",
                                "type": "position",
                                "staffName": "Ковалев А.П.",
                                "staffId": "8",
                                "is_vacant": False
                            },
                            {
                                "id": "pos-402",
                                "name": "Ассистент менеджера",
                                "type": "position",
                                "is_vacant": True
                            }
                        ]
                    }
                ]
            }
        ]
        
        # Если запрошена конкретная локация
        if location_id:
            for location in locations:
                if location["id"] == f"org-{location_id}":
                    return location
            
            # Если не нашли, возвращаем 404
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Локация с ID {location_id} не найдена"
            )
        
        # Иначе возвращаем корневую ноду с локациями
        return {
            "id": "root",
            "name": "Территориальная структура",
            "title": "Структура по локациям",
            "type": "department",
            "children": locations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении территориальной структуры: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

async def build_organization_node(db: AsyncSession, org: models.Organization) -> Dict[str, Any]:
    """Построение узла организации с рекурсивной загрузкой подразделений и должностей"""
    
    # Загружаем все подразделения организации с eager loading
    div_query = (
        select(models.Division)
        .options(
            selectinload(models.Division.children),
            selectinload(models.Division.positions),
            selectinload(models.Division.sections)
        )
        .where(
            models.Division.organization_id == org.id,
            models.Division.parent_id == None  # Только корневые подразделения
        )
    )
    
    div_result = await db.execute(div_query)
    root_divisions = div_result.scalars().all()
    
    # Создаем узел организации
    org_node = {
        "id": f"org-{org.id}",
        "name": org.name,
        "code": org.code if hasattr(org, 'code') else None,
        "type": "department",
        "org_type": org.org_type if hasattr(org, 'org_type') else None,
        "children": []
    }
    
    # Добавляем подразделения
    for division in root_divisions:
        division_node = await build_division_node(db, division)
        org_node["children"].append(division_node)
    
    return org_node

async def build_division_node(db: AsyncSession, division: models.Division) -> Dict[str, Any]:
    """Построение узла подразделения с рекурсивной загрузкой должностей"""
    
    # Создаем узел подразделения
    division_node = {
        "id": f"div-{division.id}",
        "name": division.name,
        "code": division.code if hasattr(division, 'code') else None,
        "type": "division",
        "children": []
    }
    
    # Добавляем дочерние подразделения
    if hasattr(division, 'children') and division.children:
        for child_division in division.children:
            child_node = await build_division_node(db, child_division)
            division_node["children"].append(child_node)
    
    # Загружаем должности подразделения
    if hasattr(division, 'positions') and division.positions:
        for position in division.positions:
            position_node = await build_position_node(db, position)
            division_node["children"].append(position_node)
    
    # Добавляем отделы (sections) и их должности
    if hasattr(division, 'sections') and division.sections:
        for section in division.sections:
            section_node = {
                "id": f"sec-{section.id}",
                "name": section.name,
                "code": section.code if hasattr(section, 'code') else None,
                "type": "section",
                "children": []
            }
            
            # Загружаем должности отдела с eager loading
            section_positions_query = (
                select(models.Position)
                .where(models.Position.section_id == section.id)
            )
            
            section_positions_result = await db.execute(section_positions_query)
            section_positions = section_positions_result.scalars().all()
            
            for position in section_positions:
                position_node = await build_position_node(db, position)
                section_node["children"].append(position_node)
            
            # Добавляем отдел только если есть должности
            if section_node["children"]:
                division_node["children"].append(section_node)
    
    return division_node

async def build_position_node(db: AsyncSession, position: models.Position) -> Dict[str, Any]:
    """Построение узла должности"""
    
    # Создаем узел должности
    position_node = {
        "id": f"pos-{position.id}",
        "name": position.name,
        "code": position.code if hasattr(position, 'code') else None,
        "type": "position",
        "level": position.attribute if hasattr(position, 'attribute') else None,
        "position_level": position.level if hasattr(position, 'level') else None,
        "organization_id": position.organization_id if hasattr(position, 'organization_id') else None,
        "is_vacant": True  # По умолчанию вакантна, меняется если найден сотрудник
    }
    
    # Проверяем наличие сотрудника на должности
    staff_position_query = (
        select(models.StaffPosition)
        .options(selectinload(models.StaffPosition.staff))
        .where(models.StaffPosition.position_id == position.id)
    )
    
    staff_position_result = await db.execute(staff_position_query)
    staff_position = staff_position_result.scalars().first()
    
    if staff_position and staff_position.staff:
        position_node["staffId"] = staff_position.staff.id
        position_node["staffName"] = staff_position.staff.full_name() if hasattr(staff_position.staff, 'full_name') else f"{staff_position.staff.last_name} {staff_position.staff.first_name}"
        position_node["is_vacant"] = False
    
    return position_node 