from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Базовая схема Функции
class FunctionBase(BaseModel):
    name: str
    code: str
    section_id: int
    description: Optional[str] = None
    is_active: bool = True

# Схема для создания (наследуется от Base)
class FunctionCreate(FunctionBase):
    pass

# Схема для обновления (все поля опциональны)
class FunctionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    section_id: Optional[int] = None 
    description: Optional[str] = None
    is_active: Optional[bool] = None

# Схема для чтения из БД (включает поля БД)
class FunctionInDBBase(FunctionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # Можно добавить сюда связанную секцию, если нужно ее возвращать
    # section: Optional[Section] = None # Импортировать Section из schemas.section
    
    model_config = ConfigDict(from_attributes=True)

# Финальная схема для возврата через API
class Function(FunctionInDBBase):
    pass 