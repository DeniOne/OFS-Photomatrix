from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.function import Function
from app.schemas.function import FunctionCreate, FunctionUpdate

class CRUDFunction(CRUDBase[Function, FunctionCreate, FunctionUpdate]):
    def get_by_code(self, db: Session, *, code: str) -> Optional[Function]:
        """
        Получает функцию по её уникальному коду.

        Args:
            db: Сессия базы данных.
            code: Код функции для поиска.

        Returns:
            Объект Function или None, если не найден.
        """
        return db.query(self.model).filter(self.model.code == code).first()

# Создаем экземпляр CRUD для использования в API
function = CRUDFunction(Function) 