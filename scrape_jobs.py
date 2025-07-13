import logging
import sys
import os
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app.core.database import SessionLocal
from app.services.job_scraper_service import JobScraperService

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def main():
    """
    Main function to run the job scraping process.
    """
    logger = logging.getLogger(__name__)
    logger.info("Job scraping process started.")
    
    db = None
    try:
        db = SessionLocal()
        JobScraperService.run_all_scrapers(db)
    except Exception as e:
        logger.critical(f"An uncaught exception occurred: {e}")
    finally:
        if db:
            db.close()
            logger.info("Database session closed.")
    
    logger.info("Job scraping process finished.")

if __name__ == "__main__":
    main()
