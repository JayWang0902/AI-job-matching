from fastapi import FastAPI
from app.api import auth, resume, jd, match, recommend

app = FastAPI()

# Include the routers from the different modules
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(resume.router, prefix="/resume", tags=["resume"])
app.include_router(jd.router, prefix="/jd", tags=["job description"])
app.include_router(match.router, prefix="/match", tags=["match"])
app.include_router(recommend.router, prefix="/recommend", tags=["recommendation"])
