from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID, FLOAT, JSONB
from .base import Base
from datetime import datetime
import uuid

class Job(Base):
    __tablename__ = 'jobs'

    # 内部ID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 数据来源信息
    source = Column(String(100), nullable=False, default='remoteok') # 数据来源网站
    source_id = Column(String(255), nullable=False, unique=True, index=True) # 来源网站的职位ID

    # JD核心信息
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    location = Column(String(255), nullable=True)
    url = Column(String(1024), nullable=False)

    # 新增：工作类型和远程状态
    job_type = Column(String(100), nullable=True) # e.g., 'Full-time', 'Contract'
    is_remote = Column(Boolean, nullable=True)

    # 新增：薪资信息
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), nullable=True) # e.g., 'USD', 'EUR'

    # 新增：用于存储其他非标准化数据的JSON字段
    additional_data = Column(JSONB, nullable=True)
    
    # 时间戳
    posted_at = Column(DateTime, nullable=False) # JD发布时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 用于AI匹配的字段 (预留)
    embedding = Column(ARRAY(FLOAT), nullable=True) # JD内容的向量表示

    __table_args__ = (
        # 创建一个复合唯一约束，确保同一个来源的同一个职位ID只被记录一次
        UniqueConstraint('source', 'source_id', name='uq_source_source_id'),
    )

    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}')>"
