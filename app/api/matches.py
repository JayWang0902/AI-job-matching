from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_deps import get_current_active_user
from app.models.user import User
from app.models.job_match import JobMatch
from app.services.job_matching_service import JobMatchingService
from app.schemas.match import JobMatchListResponse, JobMatchResponse, JobInMatch
import logging
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/", response_model=JobMatchListResponse)
async def get_user_matches(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数")
):
    """
    获取当前用户的岗位匹配列表
    
    返回根据简历匹配度最高的岗位列表，按匹配度降序排列。
    """
    try:
        # 返回最新一天匹配的岗位和岗位数量
        matches, total_matches_in_batch = JobMatchingService.get_matches_for_user(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        # 全部匹配历史记录
        total_matches = db.query(JobMatch).filter(JobMatch.user_id == current_user.id).count()

        # Manually construct the response to fit the schema
        match_responses = []
        for match in matches:
            job_details = JobInMatch.from_orm(match.job)
            match_response = JobMatchResponse(
                id=match.id,
                job=job_details,
                similarity_score=match.similarity_score,
                analysis=match.analysis,
                created_at=match.created_at
            )
            match_responses.append(match_response)

        return JobMatchListResponse(matches=match_responses, total=total_matches_in_batch)

    except Exception as e:
        logger.error(f"获取用户 {current_user.username} 的岗位匹配失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取岗位匹配失败")
