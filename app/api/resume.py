from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_deps import get_current_active_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/resume", tags=["resume"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """上传简历文件（需要登录）"""
    if not file.filename.endswith(('.pdf', '.doc', '.docx')):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    # TODO: 实现文件处理逻辑，关联到当前用户
    return {
        "message": "Resume uploaded successfully", 
        "filename": file.filename,
        "user_id": current_user.id,
        "username": current_user.username
    }

@router.get("/")
async def get_resumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有简历"""
    # TODO: 实现简历检索逻辑，只返回当前用户的简历
    return {
        "resumes": [],
        "user_id": current_user.id,
        "message": f"Resumes for {current_user.username}"
    }