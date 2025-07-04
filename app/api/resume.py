from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_deps import get_current_active_user
from app.models.user import User
from app.schemas.user import (
    ResumeUploadRequest, ResumeUploadResponse, ResumeResponse, 
    ResumeListResponse, ResumeMetadata
)
from app.services.resume_service import ResumeService
from app.services.resume_processing_service import resume_processing_service
from typing import Optional
import logging
from uuid import UUID

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resume", tags=["resume"])

@router.post("/upload-url", response_model=ResumeUploadResponse)
async def create_upload_url(
    upload_request: ResumeUploadRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建预签名上传URL
    
    前端调用此接口获取上传URL，然后直接上传到S3
    支持的文件格式：PDF, DOC, DOCX
    文件大小限制：10MB
    """
    try:
        # 文件名验证
        if not upload_request.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 文件扩展名验证
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_ext = '.' + upload_request.filename.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件格式。支持的格式：{', '.join(allowed_extensions)}"
            )
        
        # 文件大小验证
        if upload_request.file_size and upload_request.file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
        
        upload_response = ResumeService.create_resume_upload_url(
            db=db,
            user_id=current_user.id,
            upload_request=upload_request
        )
        
        return upload_response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建上传URL失败: {e}")
        raise HTTPException(status_code=500, detail="创建上传URL失败")

@router.put("/{resume_id}/status")
async def update_resume_status(
    resume_id: UUID,
    status: str = Query(..., description="状态：uploaded, processing, parsed, failed"),
    progress: Optional[float] = Query(None, description="上传进度 0.0-1.0"),
    error_message: Optional[str] = Query(None, description="错误信息"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新简历状态
    
    前端上传完成后调用此接口更新状态
    也可用于更新处理进度
    """
    try:
        # 状态验证
        valid_statuses = ['pending', 'uploaded', 'processing', 'parsed', 'failed']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"无效状态。有效状态：{', '.join(valid_statuses)}"
            )
        
        # 进度验证
        if progress is not None and (progress < 0.0 or progress > 1.0):
            raise HTTPException(status_code=400, detail="进度值必须在0.0-1.0之间")
        
        resume = ResumeService.update_resume_status(
            db=db,
            resume_id=resume_id,
            user_id=current_user.id,
            status=status,
            progress=progress,
            error_message=error_message
        )
        
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # If status is 'uploaded', trigger the synchronous processing
        if status == 'uploaded':
            try:
                resume_processing_service.process_resume(db=db, resume_id=resume_id)
                # We need to refresh the resume object to get the latest status
                db.refresh(resume)
            except Exception as e:
                logger.error(f"同步处理简历失败: {e}")
                # The service itself handles setting the status to 'failed'
                # but we raise an HTTP exception to inform the client.
                raise HTTPException(status_code=500, detail=f"简历处理失败: {e}")

        return {
            "message": "状态更新成功",
            "resume_id": resume_id,
            "status": resume.status,
            "progress": resume.upload_progress
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新简历状态失败: {e}")
        raise HTTPException(status_code=500, detail="更新状态失败")

@router.get("/", response_model=ResumeListResponse)
async def get_resumes(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有简历"""
    try:
        return ResumeService.get_user_resumes(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"获取简历列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取简历列表失败")

@router.get("/{resume_id}", response_model=ResumeMetadata)
async def get_resume_detail(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取单个简历详情"""
    try:
        resume = ResumeService.get_resume_by_id(
            db=db,
            resume_id=resume_id,
            user_id=current_user.id
        )
        
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        return ResumeMetadata(
            id=resume.id,
            user_id=resume.user_id,
            filename=resume.filename,
            original_filename=resume.original_filename,
            file_size=resume.file_size,
            content_type=resume.content_type,
            s3_key=resume.s3_key,
            s3_bucket=resume.s3_bucket,
            status=resume.status,
            upload_progress=resume.upload_progress,
            created_at=resume.created_at,
            updated_at=resume.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取简历详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取简历详情失败")

@router.get("/{resume_id}/download")
async def get_download_url(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取简历下载URL"""
    try:
        download_url = ResumeService.generate_download_url(
            db=db,
            resume_id=resume_id,
            user_id=current_user.id
        )
        
        if not download_url:
            raise HTTPException(status_code=404, detail="简历不存在或未上传完成")
        
        return {
            "download_url": download_url,
            "expires_in": 3600,
            "message": "下载链接1小时内有效"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成下载URL失败: {e}")
        raise HTTPException(status_code=500, detail="生成下载URL失败")

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除简历"""
    try:
        success = ResumeService.delete_resume(
            db=db,
            resume_id=resume_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        return {"message": "简历删除成功", "resume_id": resume_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除简历失败: {e}")
        raise HTTPException(status_code=500, detail="删除简历失败")

# 保留原有的直接上传接口作为备用
@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """直接上传简历文件（备用接口）"""
    if not file.filename.endswith(('.pdf', '.doc', '.docx')):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    # TODO: 实现直接上传逻辑
    return {
        "message": "请使用 /upload-url 接口获取预签名上传URL", 
        "filename": file.filename,
        "user_id": current_user.id,
        "username": current_user.username,
        "note": "推荐使用预签名URL方式上传"
    }