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
    
class InvitationCodeSchema(BaseModel):
    """
    u0421u0445u0435u043cu0430 u0434u043bu044f u0432u0430u043bu0438u0434u0430u0446u0438u0438 u043au043eu0434u0430 u043fu0440u0438u0433u043bu0430u0448u0435u043du0438u044f
    """
    code: str
    telegram_id: str 