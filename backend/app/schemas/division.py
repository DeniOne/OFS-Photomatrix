from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re
from enum import Enum

# Перечисление для типов подразделений
class DivisionType(str, Enum):
    DEPARTMENT = "DEPARTMENT"  # Департамент (верхний уровень)
    DIVISION = "DIVISION"      # Отдел (дочерний уровень)

class DivisionBase(BaseModel):
    """Базовая схема для подразделения"""
    name: str = Field(..., min_length=1, max_length=100, description="Название подразделения")
    code: str = Field(..., min_length=1, max_length=50, description="Уникальный код подразделения")
    description: Optional[str] = Field(None, description="Описание подразделения")
    organization_id: int = Field(..., description="ID организации")
    parent_id: Optional[int] = Field(None, description="ID родительского подразделения")
    is_active: bool = Field(True, description="Статус активности")
    type: DivisionType = Field(DivisionType.DEPARTMENT, description="Тип подразделения: департамент или отдел")
    
    @field_validator('code')
    def validate_code(cls, value):
        if not re.match(r'^[A-Za-z0-9_-]+$', value):
            raise ValueError("Код должен содержать только буквы, цифры, дефис и подчеркивание")
        return value

class DivisionCreate(DivisionBase):
    """Схема для создания подразделения"""
    pass

class DivisionUpdate(BaseModel):
    """Схема для обновления подразделения"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    organization_id: Optional[int] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    type: Optional[DivisionType] = None
    
    @field_validator('code')
    def validate_code(cls, value):
        if value is not None and not re.match(r'^[A-Za-z0-9_-]+$', value):
            raise ValueError("Код должен содержать только буквы, цифры, дефис и подчеркивание")
        return value

class Division(DivisionBase):
    """Схема для возврата подразделения"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DivisionWithRelations(Division):
    """Схема подразделения с включенными связями"""
    parent: Optional['DivisionWithRelations'] = None
    children: List['DivisionWithRelations'] = []
    
    class Config:
        from_attributes = True

# Для совместимости с текущим кодом - добавляем алиас для DivisionWithChildren
DivisionWithChildren = DivisionWithRelations

# Необходимо для правильной работы рекурсивных типов
DivisionWithRelations.model_rebuild() 