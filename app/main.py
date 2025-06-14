from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.api import auth, resume

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

@app.get("/")
async def root():
    return {"message": "Welcome to AI Job Matching API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
