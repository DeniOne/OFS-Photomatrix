from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    """
    Схема для токена аутентификации
    """
    access_token: str
    token_type: str
    
class TokenPayload(BaseModel):
    """
    Схема для полезной нагрузки JWT токена
    """
    sub: Optional[int] = None
    
class TokenData(BaseModel):
    """
    Данные из токена
    """
    username: str 