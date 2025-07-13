import logging
from typing import List, Dict, Any
from datetime import datetime
from app.services.job_scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

class RemoteOkScraper(BaseScraper):
    """Scraper for RemoteOK job board."""
    
    API_URL = "https://remoteok.com/api"

    def get_source_name(self) -> str:
        return 'remoteok'

    def fetch_and_normalize(self) -> List[Dict[str, Any]]:
        """
        Fetches job data from RemoteOK API and normalizes it.
        """
        raw_data = self._make_request(self.API_URL)
        
        if not raw_data or not isinstance(raw_data, list) or len(raw_data) < 2:
            logger.warning("RemoteOK API did not return valid data.")
            return []
            
        # The first item is a legal notice, skip it.
        jobs_data = raw_data[1:]
        normalized_jobs = []

        for job in jobs_data:
            if not job.get('id'):
                continue
            
            salary_currency = 'USD' if job.get('salary_min') or job.get('salary_max') else None

            normalized_job = {
                "source_id": str(job.get('id')),
                "title": job.get('position'),
                "company": job.get('company'),
                "description": job.get('description'),
                "tags": job.get('tags', []),
                "location": job.get('location'),
                "url": job.get('url'),
                "posted_at": datetime.fromtimestamp(int(job.get('epoch'))),
                "source": self.get_source_name(),

                "is_remote": True, # All jobs on RemoteOK are remote
                "salary_min": job.get('salary_min'),
                "salary_max": job.get('salary_max'),
                "salary_currency": salary_currency,
                "additional_data": {
                    "slug": job.get('slug'),
                    "apply_url": job.get('apply_url')
                }
            }
            normalized_jobs.append(normalized_job)
            
        return normalized_jobs
