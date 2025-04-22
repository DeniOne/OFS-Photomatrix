from sqlalchemy.orm import Session

from app import crud
from app.schemas.division import DivisionCreate
from app.tests.utils.utils import random_string, random_lower_string
from app.tests.utils.organization import create_random_organization

def create_random_division(db: Session, *, organization_id: int = None, parent_id: int = None) -> None:
    """
    Создает случайное подразделение для тестирования
    
    Args:
        db: Сессия базы данных
        organization_id: ID организации (если не указан, создается новая организация)
        parent_id: ID родительского подразделения (опционально)
        
    Returns:
        Созданное подразделение
    """
    if organization_id is None:
        # Создаем организацию
        organization = create_random_organization(db)
        organization_id = organization.id
        
    division_data = DivisionCreate(
        name=f"Test Division {random_string()}",
        code=f"DIV_{random_lower_string(5)}",
        description=f"Test division description {random_string(10)}",
        organization_id=organization_id,
        parent_id=parent_id,
        is_active=True
    )
    
    return crud.division.create_division(db=db, division_in=division_data) 