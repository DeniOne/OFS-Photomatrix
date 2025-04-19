from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ValueProductBase(BaseModel):
    """Базовая схема ЦКП (Ценного Конечного Продукта)"""
    name: str
    code: str
    organization_id: int
    description: Optional[str] = None
    parent_id: Optional[int] = None
    weight: float = 1.0
    completion_metrics: Dict[str, Any] = {}
    status: str = "active"
    is_active: bool = True
    
class ValueProductCreate(ValueProductBase):
    """Схема для создания ЦКП"""
    pass
    
class ValueProductUpdate(BaseModel):
    """Схема для обновления ЦКП"""
    name: Optional[str] = None
    code: Optional[str] = None
    organization_id: Optional[int] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    weight: Optional[float] = None
    completion_metrics: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    
class ValueProductInDBBase(ValueProductBase):
    """Базовая схема для ЦКП в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class ValueProduct(ValueProductInDBBase):
    """Схема для возврата ЦКП через API"""
    pass
    
class ValueProductWithChildren(ValueProduct):
    """Схема с вложенными дочерними ЦКП"""
    children: List["ValueProductWithChildren"] = []
    
ValueProductWithChildren.model_rebuild()  # Для корректной рекурсивной типизации 