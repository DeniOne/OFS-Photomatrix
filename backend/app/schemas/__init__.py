from app.schemas.token import Token, TokenPayload, ActivationResponse, UserActivation
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB, UsersPublic
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate, OrganizationWithChildren, OrganizationTree
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
    "User", "UserCreate", "UserUpdate", "UserInDB", "UsersPublic",
    "Organization", "OrganizationCreate", "OrganizationUpdate", "OrganizationWithChildren", "OrganizationTree",
    "Division", "DivisionCreate", "DivisionUpdate", "DivisionWithChildren", "DivisionWithRelations",
    "Section", "SectionCreate", "SectionUpdate",
    "Position", "PositionCreate", "PositionUpdate",
    "Staff", "StaffCreate", "StaffUpdate", "StaffCreateResponse",
    "StaffPosition", "StaffPositionCreate", "StaffPositionUpdate", 
    "Function", "FunctionCreate", "FunctionUpdate",
    "FunctionalAssignment", "FunctionalAssignmentCreate", "FunctionalAssignmentUpdate",
    "FunctionalRelation", "FunctionalRelationCreate", "FunctionalRelationUpdate",
    "Token", "TokenPayload", "ActivationResponse", "UserActivation"
] 