from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 用户注册请求模型
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# 用户登录请求模型
class UserLogin(BaseModel):
    username: str
    password: str

# 用户响应模型
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    last_active_at: datetime
    
    class Config:
        from_attributes = True

# JWT Token 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str

# Token 数据模型
class TokenData(BaseModel):
    username: Optional[str] = None