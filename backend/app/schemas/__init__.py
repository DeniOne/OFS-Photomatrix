from app.schemas.token import Token, TokenPayload
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate, OrganizationWithChildren
from app.schemas.division import Division, DivisionCreate, DivisionUpdate, DivisionWithRelations
from app.schemas.section import Section, SectionCreate, SectionUpdate
from app.schemas.position import Position, PositionCreate, PositionUpdate
from app.schemas.staff import Staff, StaffCreate, StaffUpdate, StaffCreateResponse
from app.schemas.staff_position import StaffPosition, StaffPositionCreate, StaffPositionUpdate
from app.schemas.function import Function, FunctionCreate, FunctionUpdate
from app.schemas.functional_assignment import FunctionalAssignment, FunctionalAssignmentCreate, FunctionalAssignmentUpdate
from app.schemas.functional_relation import FunctionalRelation, FunctionalRelationCreate, FunctionalRelationUpdate

# Для совместимости
DivisionWithChildren = DivisionWithRelations

# Для удобного импорта всех схем
__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Organization", "OrganizationCreate", "OrganizationUpdate", "OrganizationWithChildren",
    "Division", "DivisionCreate", "DivisionUpdate", "DivisionWithChildren", "DivisionWithRelations",
    "Section", "SectionCreate", "SectionUpdate",
    "Position", "PositionCreate", "PositionUpdate",
    "Staff", "StaffCreate", "StaffUpdate", "StaffCreateResponse",
    "StaffPosition", "StaffPositionCreate", "StaffPositionUpdate", 
    "Function", "FunctionCreate", "FunctionUpdate",
    "FunctionalAssignment", "FunctionalAssignmentCreate", "FunctionalAssignmentUpdate",
    "FunctionalRelation", "FunctionalRelationCreate", "FunctionalRelationUpdate",
    "Token", "TokenPayload"
] 