from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class OrganizationBase(BaseModel):
    """Базовая схема организации"""
    name: str
    code: str
    description: Optional[str] = None
    org_type: str = Field(..., description="Тип организации: HOLDING, LEGAL_ENTITY, etc.")
    parent_id: Optional[int] = None
    is_active: bool = True
    
class OrganizationCreate(OrganizationBase):
    """Схема для создания организации"""
    pass
    
class OrganizationUpdate(BaseModel):
    """Схема для обновления организации"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    org_type: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    
class OrganizationInDBBase(OrganizationBase):
    """Базовая схема для организации в БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class Organization(OrganizationInDBBase):
    """Схема для возврата организации через API"""
    pass
    
class OrganizationWithChildren(Organization):
    """Схема с вложенными дочерними организациями"""
    children: List["OrganizationWithChildren"] = []
    
OrganizationWithChildren.model_rebuild()  # Для корректной рекурсивной типизации 

class OrganizationTree(BaseModel):
    """Схема для древовидного отображения структуры организаций в API"""
    id: int
    name: str
    code: str
    description: Optional[str] = None
    org_type: str
    parent_id: Optional[int] = None
    is_active: bool = True
    children: List["OrganizationTree"] = []
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Холдинг",
                    "code": "HOLDING",
                    "description": "Головная организация",
                    "org_type": "HOLDING",
                    "parent_id": None,
                    "is_active": True,
                    "children": [
                        {
                            "id": 2,
                            "name": "ООО Дочерняя компания",
                            "code": "CHILD-1",
                            "description": "Дочерняя организация",
                            "org_type": "LEGAL_ENTITY",
                            "parent_id": 1,
                            "is_active": True,
                            "children": []
                        }
                    ]
                }
            ]
        }
    }
    
OrganizationTree.model_rebuild()  # Для корректной рекурсивной типизации 