from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.api import auth, resume, matches
from app.tasks import run_daily_flow

app = FastAPI(
    title="AI Job Matching API",
    description="AI-powered job matching system with user authentication",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(auth.router, tags=["auth"])
app.include_router(resume.router, tags=["resume"])
app.include_router(matches.router, tags=["matches"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Job Matching API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/debug/trigger-daily-flow", tags=["debug"])
async def trigger_daily_flow_endpoint():
    """
    Manually trigger the daily job scraping and matching flow.
    NOTE: This endpoint should be disabled or protected in production.
    """
    run_daily_flow.delay()
    return {"message": "Daily job flow has been triggered successfully. Check Celery logs for progress."}
