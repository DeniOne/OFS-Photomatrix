from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from .staff_position import StaffPosition
from .user import User

class StaffPositionBase(BaseModel):
    position_id: int
    is_primary: bool = False


class StaffPositionCreate(StaffPositionBase):
    pass


class StaffPosition(StaffPositionBase):
    id: int
    staff_id: int
    position_name: Optional[str] = None
    
    class Config:
        orm_mode = True


class StaffBase(BaseModel):
    """Базовая схема сотрудника"""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    hire_date: Optional[date] = None
    organization_id: Optional[int] = None
    user_id: Optional[int] = None
    photo_path: Optional[str] = None
    document_paths: Optional[Dict[str, str]] = None
    is_active: bool = True
    
class StaffCreate(StaffBase):
    """Схема для создания сотрудника"""
    positions: Optional[List[StaffPositionCreate]] = None
    create_user: bool = False # Флаг для создания связанного пользователя
    password: Optional[str] = None
    
class StaffUpdate(StaffBase):
    """Схема для обновления сотрудника"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    hire_date: Optional[date] = None
    user_id: Optional[int] = None
    photo_path: Optional[str] = None
    document_paths: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None
    create_user: Optional[bool] = None  # Флаг для создания связанного пользователя при обновлении
    positions: Optional[List[StaffPositionCreate]] = None
    password: Optional[str] = None
    
class StaffInDBBase(StaffBase):
    """Базовая схема для сотрудника в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class Staff(StaffInDBBase):
    """Схема для возврата сотрудника через API"""
    positions: Optional[List[StaffPosition]] = None  # Связанные должности
    user: Optional[User] = None  # Связанный пользователь
    organization_name: Optional[str] = None  # Название организации

# Новая схема для ответа при создании сотрудника с пользователем
class StaffCreateResponse(Staff):
    activation_code: Optional[str] = None 