from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PositionBase(BaseModel):
    """Базовая схема должности"""
    name: str
    code: str
    division_id: Optional[int] = None
    section_id: Optional[int] = None
    attribute: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    
class PositionCreate(PositionBase):
    """Схема для создания должности"""
    function_ids: Optional[List[int]] = []
    
class PositionUpdate(BaseModel):
    """Схема для обновления должности"""
    name: Optional[str] = None
    code: Optional[str] = None
    division_id: Optional[int] = None
    section_id: Optional[int] = None
    attribute: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    function_ids: Optional[List[int]] = None
    
class PositionInDBBase(PositionBase):
    """Базовая схема для должности в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class Position(PositionInDBBase):
    """Схема для возврата должности через API"""
    function_ids: List[int] = [] 