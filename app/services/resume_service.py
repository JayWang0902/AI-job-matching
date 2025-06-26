from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import Resume, User
from app.schemas.user import ResumeUploadRequest, ResumeUploadResponse, ResumeResponse, ResumeListResponse
from app.services.s3_service import s3_service
from typing import List, Optional
import logging
from datetime import datetime
from uuid import UUID

logger = logging.getLogger(__name__)

class ResumeService:
    """简历服务类"""
    
    @staticmethod
    def create_resume_upload_url(
        db: Session, 
        user_id: UUID, 
        upload_request: ResumeUploadRequest
    ) -> ResumeUploadResponse:
        """创建简历上传URL"""
        try:
            # 验证文件类型
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if upload_request.content_type not in allowed_types:
                raise ValueError("仅支持PDF和Word文档格式")
            
            # 生成S3键
            s3_key = s3_service.generate_s3_key(user_id, upload_request.filename)
            
            # 生成预签名上传URL
            upload_info = s3_service.generate_presigned_upload_url(
                s3_key=s3_key,
                content_type=upload_request.content_type,
                expires_in=3600
            )
            
            # 在数据库中创建简历记录
            resume = Resume(
                user_id=user_id,
                filename=s3_key.split('/')[-1],  # 存储的文件名
                original_filename=upload_request.filename,
                file_size=upload_request.file_size,
                content_type=upload_request.content_type,
                s3_key=s3_key,
                s3_bucket=s3_service.s3_bucket,
                status='pending'
            )
            
            db.add(resume)
            db.commit()
            db.refresh(resume)
            
            return ResumeUploadResponse(
                resume_id=resume.id,
                upload_url=upload_info['upload_url'],
                upload_fields=upload_info['upload_fields'],
                expires_in=upload_info['expires_in']
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"创建上传URL失败: {e}")
            raise Exception(f"创建上传URL失败: {str(e)}")
    
    @staticmethod
    def update_resume_status(
        db: Session, 
        resume_id: UUID, 
        user_id: UUID, 
        status: str, 
        progress: float = None,
        error_message: str = None
    ) -> Optional[Resume]:
        """更新简历状态"""
        resume = db.query(Resume).filter(
            and_(Resume.id == resume_id, Resume.user_id == user_id)
        ).first()
        
        if not resume:
            return None
        
        resume.status = status
        resume.updated_at = datetime.utcnow()
        
        if progress is not None:
            resume.upload_progress = progress
        
        if error_message:
            resume.error_message = error_message
        
        # 如果状态为uploaded，检查文件并更新文件大小
        if status == 'uploaded':
            if s3_service.check_file_exists(resume.s3_key):
                file_size = s3_service.get_file_size(resume.s3_key)
                if file_size:
                    resume.file_size = file_size
                resume.upload_progress = 1.0
            else:
                resume.status = 'failed'
                resume.error_message = '文件上传失败'
        
        db.commit()
        db.refresh(resume)
        return resume
    
    @staticmethod
    def get_user_resumes(db: Session, user_id: UUID, skip: int = 0, limit: int = 10) -> ResumeListResponse:
        """获取用户的简历列表"""
        resumes = db.query(Resume).filter(Resume.user_id == user_id)\
                   .order_by(Resume.created_at.desc())\
                   .offset(skip).limit(limit).all()
        
        total = db.query(Resume).filter(Resume.user_id == user_id).count()
        
        resume_responses = [
            ResumeResponse(
                id=resume.id,
                filename=resume.original_filename,
                original_filename=resume.original_filename,
                file_size=resume.file_size,
                status=resume.status,
                upload_progress=resume.upload_progress,
                uploaded_at=resume.created_at
            )
            for resume in resumes
        ]
        
        return ResumeListResponse(
            resumes=resume_responses,
            total=total,
            user_id=user_id
        )
    
    @staticmethod
    def get_resume_by_id(db: Session, resume_id: UUID, user_id: UUID) -> Optional[Resume]:
        """根据ID获取简历"""
        return db.query(Resume).filter(
            and_(Resume.id == resume_id, Resume.user_id == user_id)
        ).first()
    
    @staticmethod
    def delete_resume(db: Session, resume_id: UUID, user_id: UUID) -> bool:
        """删除简历"""
        resume = db.query(Resume).filter(
            and_(Resume.id == resume_id, Resume.user_id == user_id)
        ).first()
        
        if not resume:
            return False
        
        try:
            # 删除S3文件
            s3_service.delete_file(resume.s3_key)
            
            # 删除数据库记录
            db.delete(resume)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"删除简历失败: {e}")
            return False
    
    @staticmethod
    def generate_download_url(db: Session, resume_id: UUID, user_id: UUID) -> Optional[str]:
        """生成下载URL"""
        resume = ResumeService.get_resume_by_id(db, resume_id, user_id)
        
        if not resume or resume.status != 'uploaded':
            return None
        
        try:
            return s3_service.generate_download_url(resume.s3_key)
        except Exception as e:
            logger.error(f"生成下载URL失败: {e}")
            return None