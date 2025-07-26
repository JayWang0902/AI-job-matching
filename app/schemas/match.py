from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

# Schema for the Job details nested within a match response
class JobInMatch(BaseModel):
    id: UUID
    title: str
    company: Optional[str]
    location: Optional[str]
    url: str
    posted_at: datetime
    source: str

    class Config:
        from_attributes = True

# Schema for a single Job Match item
class JobMatchResponse(BaseModel):
    id: UUID
    job: JobInMatch
    similarity_score: float
    analysis: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Schema for the list of all job matches for a user
class JobMatchListResponse(BaseModel):
    matches: List[JobMatchResponse]
    total: int
