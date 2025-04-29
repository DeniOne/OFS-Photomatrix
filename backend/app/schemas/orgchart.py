from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field

# Базовая схема для сотрудника в ответе
class BackendStaffNode(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    position_name: Optional[str] = None # Название должности
    type: Literal['STAFF'] = 'STAFF' # Фиксированный тип

    class Config:
        orm_mode = True # Для совместимости с ORM

# Базовая схема для подразделения в ответе
class BackendDivisionNodeBase(BaseModel):
    id: int
    name: str
    type: Literal['DEPARTMENT', 'DIVISION']
    code: Optional[str] = None

    class Config:
        orm_mode = True

# Рекурсивная схема для дочерних элементов
class BackendDivisionNode(BackendDivisionNodeBase):
    children: Optional[List[Union['BackendDivisionNode', BackendStaffNode]]] = None # Дети могут быть подразделениями или сотрудниками

# Обновляем ссылку на саму себя после определения
BackendDivisionNode.update_forward_refs()

# Тип для корневого элемента (должен быть подразделением)
BackendOrgChartData = BackendDivisionNode 
# Тип для любого узла в дереве
BackendNode = Union[BackendDivisionNode, BackendStaffNode] 