import logging
from sqlalchemy.orm import Session
from app.models.job import Job
from app.services.job_scrapers.remoteok import RemoteOkScraper
from app.services.job_scrapers.arbeitnow import ArbeitnowScraper
from app.services.job_processing_service import JobProcessingService

logger = logging.getLogger(__name__)

class JobScraperService:
    """
    A service to orchestrate various job scrapers and save data to the database.
    """
    
    # A list of all scraper instances to be run.
    SCRAPERS = [
        RemoteOkScraper()
        # ArbeitnowScraper(),
    ]

    @classmethod
    def run_all_scrapers(cls, db: Session):
        """
        Iterates through all registered scrapers, fetches data, saves new
        job postings, and generates embeddings for them.
        """
        total_new_jobs = 0
        for scraper in cls.SCRAPERS:
            source_name = scraper.get_source_name()
            logger.info(f"Starting to scrape jobs from {source_name}...")
            
            new_jobs_to_process = []
            try:
                normalized_jobs = scraper.fetch_and_normalize()
                if not normalized_jobs:
                    logger.info(f"No jobs found from {source_name}.")
                    continue

                for job_data in normalized_jobs[:5]:
                    # Check if the job already exists to avoid duplicates
                    exists = db.query(Job).filter_by(
                        source=source_name,
                        source_id=job_data['source_id']
                    ).first()

                    if not exists:
                        new_job = Job(**job_data)
                        db.add(new_job)
                        new_jobs_to_process.append(new_job)
                
                if new_jobs_to_process:
                    # Flush to assign IDs before processing embeddings
                    db.flush()

                    logger.info(f"Found {len(new_jobs_to_process)} new jobs from {source_name}. Generating embeddings...")
                    for job in new_jobs_to_process:
                        try:
                            JobProcessingService.process_job_embedding(db, job)
                        except Exception as e:
                            logger.error(f"Error processing embedding for job {job.id} from {source_name}: {e}")
                    
                    db.commit()
                    logger.info(f"Successfully added {len(new_jobs_to_process)} new jobs and their embeddings from {source_name}.")
                    total_new_jobs += len(new_jobs_to_process)
                else:
                    logger.info(f"No new jobs to add from {source_name}.")

            except Exception as e:
                logger.error(f"Failed to scrape from {source_name}: {e}")
                db.rollback()
        
        logger.info(f"Scraping finished. Total new jobs added: {total_new_jobs}.")
