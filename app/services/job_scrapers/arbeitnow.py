import logging
from typing import List, Dict, Any
from datetime import datetime
from app.services.job_scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

class ArbeitnowScraper(BaseScraper):
    """Scraper for Arbeitnow job board."""
    
    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    def get_source_name(self) -> str:
        return 'arbeitnow'

    def fetch_and_normalize(self) -> List[Dict[str, Any]]:
        """
        Fetches job data from Arbeitnow API and normalizes it.
        """
        response_data = self._make_request(self.API_URL)
        
        if not response_data or 'data' not in response_data or not isinstance(response_data['data'], list):
            logger.warning("Arbeitnow API did not return valid data.")
            return []
            
        jobs_data = response_data['data']
        normalized_jobs = []

        for job in jobs_data:
            if not job.get('slug'): # Using slug as a unique identifier
                continue

            job_types = job.get('job_types', [])
            job_type_str = ", ".join(job_types) if job_types else None
            
            normalized_job = {
                "source_id": job.get('slug'),
                "title": job.get('title'),
                "company": job.get('company_name'),
                "description": job.get('description'),
                "tags": job.get('tags', []),
                "location": job.get('location'),
                "url": job.get('url'),
                "posted_at": datetime.fromtimestamp(int(job.get('created_at'))),
                "source": self.get_source_name(),

                "job_type": job_type_str,
                "is_remote": job.get('remote')
            }
            normalized_jobs.append(normalized_job)
            
        return normalized_jobs
