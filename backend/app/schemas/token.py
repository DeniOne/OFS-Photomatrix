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

class UserActivation(BaseModel):
    activation_code: str
    password: str
    password_confirm: Optional[str] = None
    
class ActivationResponse(BaseModel):
    message: str
    is_active: bool
    access_token: Optional[str] = None
    token_type: Optional[str] = None 