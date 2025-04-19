from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FunctionBase(BaseModel):
    """Базовая схема функции"""
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    
class FunctionCreate(FunctionBase):
    """Схема для создания функции"""
    pass
    
class FunctionUpdate(BaseModel):
    """Схема для обновления функции"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    
class FunctionInDBBase(FunctionBase):
    """Базовая схема для функции в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class Function(FunctionInDBBase):
    """Схема для возврата функции через API"""
    pass 