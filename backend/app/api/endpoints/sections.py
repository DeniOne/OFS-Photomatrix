from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.deps import get_current_active_user
from app.crud import section as crud_section
from app.crud import division as crud_division
from app.models.user import User
from app.schemas.section import Section, SectionCreate, SectionUpdate

router = APIRouter()

@router.get("/", response_model=List[Section])
async def read_sections(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    division_id: Optional[int] = Query(None, description="Фильтр по подразделению"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить список отделов с возможностью фильтрации
    """
    if division_id:
        sections = await crud_section.get_by_division(
            db, division_id=division_id, skip=skip, limit=limit
        )
    else:
        sections = await crud_section.get_multi(
            db, skip=skip, limit=limit
        )
    return sections

@router.post("/", response_model=Section)
async def create_section(
    *,
    db: AsyncSession = Depends(get_db),
    section_in: SectionCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Создать новый отдел
    """
    # Проверяем существование подразделения (департамента)
    division = await crud_division.get(db, id=section_in.division_id)
    if not division:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Родительское подразделение (департамент) не найдено",
        )
    # Дополнительная проверка: убедимся, что родитель - это департамент
    # Импортируй DivisionType из app.models.division или app.types.division если еще не импортирован
    # from app.models.division import DivisionType # Пример импорта
    # if division.type != DivisionType.DEPARTMENT:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Родителем отдела может быть только департамент.",
    #     )
        
    # Проверяем уникальность кода в рамках подразделения
    existing_section = await crud_section.get_by_code_and_division(
        db, code=section_in.code, division_id=section_in.division_id
    )
    if existing_section:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отдел с таким кодом уже существует в данном подразделении",
        )
            
    return await crud_section.create(db, obj_in=section_in)

@router.get("/{id}", response_model=Section)
async def read_section(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получить отдел по ID
    """
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отдел не найден",
        )
    return section

@router.put("/{id}", response_model=Section)
async def update_section(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    section_in: SectionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить отдел
    """
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отдел не найден",
        )
        
    # Если меняется подразделение или код, проверяем уникальность кода в рамках подразделения
    if (section_in.code and section_in.code != section.code) or \
       (section_in.division_id and section_in.division_id != section.division_id):
        division_id = section_in.division_id or section.division_id
        code = section_in.code or section.code
        existing_section = await crud_section.get_by_code_and_division(
            db, code=code, division_id=division_id
        )
        if existing_section and existing_section.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отдел с таким кодом уже существует в данном подразделении",
            )
            
    # Если меняется подразделение, проверяем его существование
    if section_in.division_id and section_in.division_id != section.division_id:
        division = await crud_division.division.get(db, id=section_in.division_id)
        if not division:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подразделение не найдено",
            )
            
    return await crud_section.update(db, db_obj=section, obj_in=section_in)

@router.delete("/{id}", response_model=Section)
async def delete_section(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить отдел
    """
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отдел не найден",
        )
        
    # Здесь можно добавить дополнительные проверки, например, на наличие должностей связанных с этим отделом
    
    return await crud_section.remove(db, id=id) 