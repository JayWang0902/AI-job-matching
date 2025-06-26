from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

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
    id: UUID
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

# 简历上传相关Schema
class ResumeUploadRequest(BaseModel):
    filename: str
    content_type: str = "application/pdf"
    file_size: Optional[int] = None

class ResumeUploadResponse(BaseModel):
    resume_id: UUID
    upload_url: str
    upload_fields: dict
    expires_in: int = 3600  # 1小时过期

class ResumeMetadata(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    original_filename: str
    file_size: Optional[int]
    content_type: str
    s3_key: str
    s3_bucket: str
    status: str  # uploaded, processing, parsed, failed
    upload_progress: float = 0.0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ResumeResponse(BaseModel):
    id: UUID
    filename: str
    original_filename: str
    file_size: Optional[int]
    status: str
    upload_progress: float
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class ResumeListResponse(BaseModel):
    resumes: list[ResumeResponse]
    total: int
    user_id: UUID