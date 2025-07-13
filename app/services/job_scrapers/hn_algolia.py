import logging
from typing import List, Dict, Any
from datetime import datetime
from app.services.job_scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

class HnAlgoliaScraper(BaseScraper):
    """Scraper for Hacker News jobs via Algolia API."""
    
    API_URL = "http://hn.algolia.com/api/v1/search_by_date?tags=job"

    def get_source_name(self) -> str:
        return 'hn_algolia'

    def fetch_and_normalize(self) -> List[Dict[str, Any]]:
        """
        Fetches job data from HN Algolia API and normalizes it.
        """
        response_data = self._make_request(self.API_URL)
        
        if not response_data or 'hits' not in response_data or not isinstance(response_data['hits'], list):
            logger.warning("HN Algolia API did not return valid data.")
            return []
            
        jobs_data = response_data['hits']
        normalized_jobs = []

        for job in jobs_data:
            # Ensure the item has a unique ID and a title
            if not job.get('objectID') or not job.get('title'):
                continue

            # HN API doesn't provide a company name. We use the author as a substitute.
            # Description is also often missing, so we can use the title.
            normalized_job = {
                "source_id": str(job.get('objectID')),
                "title": job.get('title'),
                "company": job.get('author'),
                "description": job.get('story_text') or job.get('title'),
                "tags": job.get('_tags', []),
                "location": None,  # HN jobs are often remote, but location is not specified
                "url": job.get('url'),
                "posted_at": datetime.fromtimestamp(int(job.get('created_at_i'))),
                "source": self.get_source_name()
            }
            normalized_jobs.append(normalized_job)
            
        return normalized_jobs