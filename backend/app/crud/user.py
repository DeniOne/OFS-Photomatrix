import secrets
from typing import Any, Dict, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

def generate_activation_code(length: int = 32) -> str:
    """Генерирует безопасный случайный код активации."""
    return secrets.token_urlsafe(length)

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD операции для пользователей"""
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        query = select(User).filter(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_activation_code(self, db: AsyncSession, *, code: str) -> Optional[User]:
        """Получить пользователя по коду активации"""
        query = select(User).filter(User.activation_code == code)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, *, obj_in: UserCreate, commit: bool = True) -> User:
        """Создать нового пользователя.
        Если пароль не предоставлен, генерируется код активации.
        
        Args:
            db: Сессия БД
            obj_in: Данные для создания пользователя
            commit: Флаг, указывающий, нужно ли коммитить транзакцию (True по умолчанию)
        """
        try:
            create_data = obj_in.model_dump() # Используем model_dump для Pydantic v2
        except AttributeError:
            # Фоллбэк для Pydantic v1
            create_data = obj_in.dict()
        
        hashed_password = None
        activation_code = None

        if obj_in.password is not None:
            hashed_password = get_password_hash(obj_in.password)
        else:
            # Генерируем уникальный код активации
            while True:
                activation_code = generate_activation_code()
                existing_user = await self.get_by_activation_code(db=db, code=activation_code)
                if not existing_user:
                    break
        
        # Убираем пароль из данных для создания объекта модели
        # т.к. в модели нет поля password, а есть hashed_password
        create_data.pop('password', None) 

        db_obj = User(
            **create_data, 
            hashed_password=hashed_password,
            activation_code=activation_code
        )
        
        db.add(db_obj)
        
        if commit:
            await db.commit()
            await db.refresh(db_obj)
        
        return db_obj
    
    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Обновить пользователя, хешируя пароль если он предоставлен"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            # При обновлении с паролем, вероятно, нужно деактивировать старый код?
            # update_data["activation_code"] = None 
            # Пока не будем трогать код при обычном обновлении
            
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def activate_user(self, db: AsyncSession, *, user: User, password: str) -> User:
        """Активирует пользователя: устанавливает пароль и удаляет код активации."""
        hashed_password = get_password_hash(password)
        user.hashed_password = hashed_password
        user.activation_code = None
        user.is_active = True # Можно явно активировать пользователя здесь
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        # Если у пользователя нет пароля (он не активирован), не аутентифицируем
        if not user.hashed_password:
            return None 
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def is_active(self, user: User) -> bool:
        """Проверка активности пользователя"""
        return user.is_active
    
    async def is_superuser(self, user: User) -> bool:
        """Проверка суперпользователя"""
        return user.is_superuser

# Создание синглтона для использования в приложении
user = CRUDUser(User) 