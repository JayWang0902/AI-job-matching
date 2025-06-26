from sqlalchemy import Column, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

class Resume(Base):
    __tablename__ = 'resumes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    filename = Column(String(255), nullable=False)  # 存储在S3的文件名
    original_filename = Column(String(255), nullable=False) # 用户上传的原始文件名
    file_size = Column(Integer, nullable=True) # 文件大小，单位为字节
    content_type = Column(String(100), nullable=False, default='application/pdf')
    s3_key = Column(String(500), nullable=False) # S3存储的对象键
    s3_bucket = Column(String(100), nullable=False) # S3存储桶名称
    status = Column(String(50), nullable=False, default='pending') # 状态: pending, uploaded, processing, parsed, failed
    upload_progress = Column(Float, default=0.0) # 上传进度，范围0.0到1.0
    error_message = Column(Text, nullable=True) # 错误信息，如果有的话
    parsed_content = Column(Text, nullable=True) # 解析后的内容，如果有的话
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联到用户
    user = relationship("User", back_populates="resumes")
    
    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename={self.filename}, status={self.status})>"

# 在User模型中添加与Resume的关系
User.resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
