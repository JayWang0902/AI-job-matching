import logging
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.job_match import JobMatch
from app.services.openai_service import get_openai_client
from typing import List
import openai
from sqlalchemy import func
from pgvector.sqlalchemy import Vector as PgVector
from datetime import datetime, timedelta, timezone
from app.prompts import MATCH_ANALYSIS_PROMPT 

logger = logging.getLogger(__name__)

class JobMatchingService:
    """
    核心服务，用于根据用户简历匹配最合适的岗位
    """

    @classmethod
    def find_and_analyze_matches_for_user(cls, db: Session, user: User, top_k: int = 3, days: int = 1):
        """
        为单个用户查找并分析最匹配的top_k个岗位
        """
        # 1. 获取用户最新的、已生成向量的简历
        latest_resume = db.query(Resume).filter(
            Resume.user_id == user.id,
            Resume.embedding.isnot(None),
            Resume.status == 'parsed'
        ).order_by(Resume.created_at.desc()).first()

        if not latest_resume:
            logger.info(f"用户 {user.username} (ID: {user.id}) 没有可用于匹配的简历。")
            return

        logger.info(f"开始为用户 {user.username} (ID: {user.id}) 匹配岗位，使用简历 ID: {latest_resume.id}")

        # 2. 在jobs表中进行向量相似度搜索
        # 使用 L2 距离作为例子，cosine 距离 (cosine_distance) 通常更适合文本向量
        now_utc = datetime.now(timezone.utc) # 获取今天的日期
        start_datetime = now_utc - timedelta(days=days) # 计算起始日期，days默认为1天
        
        # -- 新增诊断日志 --
        # 检查在指定时间范围内，有多少岗位以及多少岗位有向量
        total_jobs_in_range = db.query(Job).filter(Job.created_at >= start_datetime).count()
        jobs_with_embedding_in_range = db.query(Job).filter(
            Job.created_at >= start_datetime,
            Job.embedding.isnot(None)
        ).count()
        
        jobs_missing_embedding = total_jobs_in_range - jobs_with_embedding_in_range

        logger.info(f"诊断信息：在过去 {days} 天内，总共找到 {total_jobs_in_range} 个岗位。其中 {jobs_with_embedding_in_range} 个有向量。")

        if jobs_missing_embedding > 0:
            logger.warning(f"发现 {jobs_missing_embedding} 个岗位在时间范围内缺失向量，这可能影响匹配结果的完整性。")
        # -- 诊断日志结束 --
        
        similar_jobs = db.query(
            Job,
            Job.embedding.cosine_distance(latest_resume.embedding).label('distance')
        ).filter(
            Job.embedding.isnot(None),
            Job.created_at >= start_datetime ## 只匹配当天创建的岗位
        ).order_by('distance').limit(top_k).all()

        if not similar_jobs:
            logger.info(f"没有找到与用户 {user.username} 的简历匹配的岗位。")
            return

        # 3. 清理该简历之前的匹配记录
        # db.query(JobMatch).filter(JobMatch.resume_id == latest_resume.id).delete()
        # db.commit()
        # logger.info(f"已清理用户 {user.username} 简历 {latest_resume.id} 的旧匹配记录。")

        # 4. 为每个匹配的岗位生成AI分析并存储
        for job, distance in similar_jobs:
            try:
                # 检查是否已存在该用户和该职位的匹配记录
                existing_match = db.query(JobMatch).filter_by(user_id=user.id, job_id=job.id).first()
                if existing_match:
                    logger.info(f"用户 {user.username} 与岗位 {job.title} (Job ID: {job.id}) 的匹配已存在，跳过。")
                    continue

                analysis = cls._generate_match_analysis(
                    resume_content=latest_resume.parsed_content,
                    job_description=job.description
                )
                
                new_match = JobMatch(
                    user_id=user.id,
                    resume_id=latest_resume.id,
                    job_id=job.id,
                    similarity_score=1 - distance,  # 将距离转换为相似度 (1-cos距离)
                    analysis=analysis
                )
                db.add(new_match)
                logger.info(f"为用户 {user.username} 创建了新的岗位匹配: {job.title} (Job ID: {job.id})")

            except Exception as e:
                logger.error(f"为岗位 {job.id} 生成AI分析或创建匹配记录时失败: {e}")
                continue
        
        db.commit()
        logger.info(f"成功为用户 {user.username} 生成了 {len(similar_jobs)} 条新的岗位匹配。")

    @staticmethod
    def _generate_match_analysis(resume_content: str, job_description: str) -> str:
        """
        使用OpenAI生成简历与岗位JD的匹配分析
        """
        prompt = MATCH_ANALYSIS_PROMPT.format(
            resume_content=resume_content[:4000],
            job_description=job_description[:4000]
        )
        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "你是一位专业的HR专家，擅长精准地分析候选人与岗位的匹配度。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200,
            )
            analysis = response.choices[0].message.content.strip()
            return analysis
        except openai.APIError as e:
            logger.error(f"OpenAI API 调用失败: {e}")
            raise  # 重新抛出异常，让上层调用者处理
        except Exception as e:
            logger.error(f"生成AI分析时发生未知错误: {e}")
            raise

    @classmethod
    def run_matching_for_all_users(cls, db: Session):
        """
        dddddd
        为所有活跃用户执行岗位匹配流程(目前应该没有调用这个方法，在tasks.py里用celery并行跑)
        """
        logger.info("开始为所有活跃用户执行每日岗位匹配...")
        active_users = db.query(User).filter(User.is_active == True).all()
        
        if not active_users:
            logger.info("没有活跃用户，跳过岗位匹配。")
            return

        logger.info(f"找到了 {len(active_users)} 位活跃用户。")
        
        for user in active_users:
            try:
                cls.find_and_analyze_matches_for_user(db, user)
            except Exception as e:
                logger.error(f"为用户 {user.username} (ID: {user.id}) 匹配岗位时发生严重错误: {e}")
                # 即使单个用户失败，也继续为其他用户匹配
                continue
        
        logger.info("所有活跃用户的岗位匹配流程执行完毕。")

    @classmethod
    def get_matches_for_user(cls, db: Session, user_id: str, skip: int = 0, limit: int = 10) -> tuple[List[JobMatch], int]:
        """
        获取指定用户的最新一批岗位匹配列表和总数
        """
        # 找到该用户最新一次匹配的时间戳
        # 我们假设同一批次的匹配 resume_id 是相同的
        latest_match_subquery = db.query(JobMatch.resume_id)\
            .filter(JobMatch.user_id == user_id)\
            .order_by(JobMatch.created_at.desc())\
            .limit(1).subquery()

        # 构建查询，只获取最新一批的匹配
        query = db.query(JobMatch).filter(
            JobMatch.user_id == user_id,
            JobMatch.resume_id.in_(latest_match_subquery)
        )

        # 获取这批次的总数用于分页
        total = query.count()

        # 获取分页后的结果
        matches = query.order_by(JobMatch.similarity_score.desc())\
            .offset(skip).limit(limit).all()
            
        return matches, total
