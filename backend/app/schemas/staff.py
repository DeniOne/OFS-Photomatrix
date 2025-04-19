from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class StaffBase(BaseModel):
    """Базовая схема сотрудника"""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    hire_date: Optional[date] = None
    user_id: Optional[int] = None
    photo_path: Optional[str] = None
    document_paths: Optional[Dict[str, str]] = None
    is_active: bool = True
    
class StaffCreate(StaffBase):
    """Схема для создания сотрудника"""
    create_user: bool = False # Флаг для создания связанного пользователя
    
class StaffUpdate(BaseModel):
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
    
class StaffInDBBase(StaffBase):
    """Базовая схема для сотрудника в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class Staff(StaffInDBBase):
    """Схема для возврата сотрудника через API"""
    pass 

# Новая схема для ответа при создании сотрудника с пользователем
class StaffCreateResponse(Staff):
    activation_code: Optional[str] = None 