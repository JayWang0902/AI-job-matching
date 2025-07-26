from sqlalchemy import Column, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.models.base import Base

class JobMatch(Base):
    __tablename__ = 'job_matches'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey('resumes.id'), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=False, index=True)
    
    similarity_score = Column(Float, nullable=False)
    analysis = Column(Text, nullable=True)
    is_viewed = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="matches")
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")

    def __repr__(self):
        return f"<JobMatch(user_id={self.user_id}, job_id={self.job_id}, score={self.similarity_score:.4f})>"
