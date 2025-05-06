from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
import logging

from app import models, schemas
from app.api import deps

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=Dict[str, Any])
async def get_org_chart(
    db: AsyncSession = Depends(deps.get_db),
    org_id: Optional[int] = None,
    # current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Получение полной организационной структуры в виде дерева для построения диаграммы.
    
    Включает:
    - Организации
    - Подразделения (Департаменты, Отделы)
    - Должности
    - Сотрудников, привязанных к должностям
    """
    logger.info(f"Запрос на получение организационной диаграммы. org_id={org_id}")
    
    try:
        # Загружаем корневые организации
        if org_id:
            # Если указан org_id, загружаем только конкретную организацию
            org_query = (
                select(models.Organization)
                .options(
                    selectinload(models.Organization.divisions)
                )
                .where(models.Organization.id == org_id)
            )
        else:
            # Иначе загружаем все корневые организации
            org_query = (
                select(models.Organization)
                .options(
                    selectinload(models.Organization.divisions)
                )
                .where(models.Organization.parent_id == None)
            )
        
        org_result = await db.execute(org_query)
        organizations = org_result.scalars().all()
        
        if not organizations:
            if org_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Организация с ID {org_id} не найдена"
                )
            else:
                # Если нет корневых организаций, создаем корневую ноду
                return {
                    "id": "root",
                    "name": "Организационная структура",
                    "title": "Структура не определена",
                    "type": "department",
                    "children": []
                }
        
        # Перебираем организации для построения дерева
        tree_nodes = []
        
        for org in organizations:
            org_node = await build_organization_node(db, org)
            tree_nodes.append(org_node)
        
        # Если запрошена конкретная организация, возвращаем только ее дерево
        if org_id and tree_nodes:
            return tree_nodes[0]
        
        # Иначе возвращаем корневую ноду с детьми
        return {
            "id": "root",
            "name": "Организационная структура",
            "title": "Корпоративная структура",
            "type": "department",
            "children": tree_nodes
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении организационной структуры: {str(e)}", exc_info=True)
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
                "type": "division",
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
    
    return position_node 