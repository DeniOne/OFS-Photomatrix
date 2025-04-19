from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SectionBase(BaseModel):
    """Базовая схема отдела"""
    name: str
    code: str
    division_id: int
    description: Optional[str] = None
    is_active: bool = True
    
class SectionCreate(SectionBase):
    """Схема для создания отдела"""
    pass
    
class SectionUpdate(BaseModel):
    """Схема для обновления отдела"""
    name: Optional[str] = None
    code: Optional[str] = None
    division_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    
class SectionInDBBase(SectionBase):
    """Базовая схема для отдела в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class Section(SectionInDBBase):
    """Схема для возврата отдела через API"""
    pass 