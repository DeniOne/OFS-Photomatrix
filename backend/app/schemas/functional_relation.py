from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FunctionalRelationBase(BaseModel):
    """Базовая схема функциональных отношений между должностями"""
    source_id: int
    target_id: int
    relation_type: str
    weight: float = 1.0
    description: Optional[str] = None
    
class FunctionalRelationCreate(FunctionalRelationBase):
    """Схема для создания функционального отношения"""
    pass
    
class FunctionalRelationUpdate(BaseModel):
    """Схема для обновления функционального отношения"""
    source_id: Optional[int] = None
    target_id: Optional[int] = None
    relation_type: Optional[str] = None
    weight: Optional[float] = None
    description: Optional[str] = None
    
class FunctionalRelationInDBBase(FunctionalRelationBase):
    """Базовая схема для функционального отношения в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class FunctionalRelation(FunctionalRelationInDBBase):
    """Схема для возврата функционального отношения через API"""
    pass 