from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class FunctionalAssignmentBase(BaseModel):
    """Базовая схема назначения функции на должность"""
    position_id: int
    function_id: int
    percentage: int = 100
    is_primary: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
class FunctionalAssignmentCreate(FunctionalAssignmentBase):
    """Схема для создания назначения функции"""
    pass
    
class FunctionalAssignmentUpdate(BaseModel):
    """Схема для обновления назначения функции"""
    position_id: Optional[int] = None
    function_id: Optional[int] = None
    percentage: Optional[int] = None
    is_primary: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
class FunctionalAssignmentInDBBase(FunctionalAssignmentBase):
    """Базовая схема для назначения функции в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class FunctionalAssignment(FunctionalAssignmentInDBBase):
    """Схема для возврата назначения функции через API"""
    pass 