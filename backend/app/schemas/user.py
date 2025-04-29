from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    
class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: Optional[str] = Field(None, min_length=8)
    
class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    
class UserInDBBase(UserBase):
    """Базовая схема для пользователя в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class User(UserInDBBase):
    """Схема для возврата пользователя через API"""
    pass
    
class UserActivate(BaseModel):
    activation_code: str
    password: str = Field(..., min_length=8)
    
class UserInDB(UserInDBBase):
    """Схема для внутреннего использования с хеш-паролем"""
    hashed_password: Optional[str]

# Новая схема для пагинированного ответа
class UsersPublic(BaseModel):
    data: List[User]
    total: int 