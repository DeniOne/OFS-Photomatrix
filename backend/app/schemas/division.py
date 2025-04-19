from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DivisionBase(BaseModel):
    """Базовая схема подразделения"""
    name: str
    code: str
    organization_id: int
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True
    
class DivisionCreate(DivisionBase):
    """Схема для создания подразделения"""
    pass
    
class DivisionUpdate(BaseModel):
    """Схема для обновления подразделения"""
    name: Optional[str] = None
    code: Optional[str] = None
    organization_id: Optional[int] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    
class DivisionInDBBase(DivisionBase):
    """Базовая схема для подразделения в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class Division(DivisionInDBBase):
    """Схема для возврата подразделения через API"""
    pass
    
class DivisionWithChildren(Division):
    """Схема с вложенными дочерними подразделениями"""
    children: List["DivisionWithChildren"] = []
    
DivisionWithChildren.model_rebuild()  # Для корректной рекурсивной типизации 