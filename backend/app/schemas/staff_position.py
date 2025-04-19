from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class StaffPositionBase(BaseModel):
    """Базовая схема назначения сотрудника на должность"""
    staff_id: int
    position_id: int
    is_primary: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
class StaffPositionCreate(StaffPositionBase):
    """Схема для создания назначения"""
    pass
    
class StaffPositionUpdate(BaseModel):
    """Схема для обновления назначения"""
    staff_id: Optional[int] = None
    position_id: Optional[int] = None
    is_primary: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
class StaffPositionInDBBase(StaffPositionBase):
    """Базовая схема для назначения в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class StaffPosition(StaffPositionInDBBase):
    """Схема для возврата назначения через API"""
    pass 