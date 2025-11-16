from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here so alembic can detect them
from app.models.user import User  # noqa: F401
from app.models.job import Job  # noqa: F401
from app.models.job_match import JobMatch  # noqa: F401