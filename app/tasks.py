from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.job_scraper_service import JobScraperService
from app.services.job_matching_service import JobMatchingService
from app.models.user import User
from celery import group, chain
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

# Default number of top job matches to return for each user
# This can be adjusted based on application requirements.
top_k = 1
# Default limit for the number of jobs to scrape from each source
limit_per_source = 5

@celery_app.task(name="app.tasks.scrape_all_jobs")
def scrape_all_jobs():
    """
    Celery task to scrape jobs from all configured sources.
    """
    logger.info("Starting job scraping task...")
    db = SessionLocal()
    try:
        JobScraperService.run_all_scrapers(db, limit_per_source)
        logger.info("Job scraping task finished successfully.")
    except Exception as e:
        logger.error(f"Job scraping task failed: {e}", exc_info=True)
        raise
    finally:
        db.close()

@celery_app.task(name="app.tasks.match_jobs_for_user")
def match_jobs_for_user(user_id_str: str):
    """
    Celery task to find and analyze job matches for a single user.
    """
    logger.info(f"Starting job matching task for user ID: {user_id_str}")
    db = SessionLocal()
    try:
        user_id = UUID(user_id_str)
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            JobMatchingService.find_and_analyze_matches_for_user(db, user, top_k)
            logger.info(f"Job matching task for user ID: {user_id_str} finished successfully.")
        else:
            logger.warning(f"User with ID {user_id_str} not found for job matching.")
    except Exception as e:
        logger.error(f"Job matching task for user ID {user_id_str} failed: {e}", exc_info=True)
        raise
    finally:
        db.close()

@celery_app.task(name="app.tasks.run_daily_flow")
def run_daily_flow():
    """
    Main scheduled Celery task to run the entire daily flow:
    1. Scrape all jobs.
    2. For each active user, run the job matching task in parallel.
    """
    logger.info("Starting daily job matching flow...")
    
    # The scraping task is the first step.
    # The matching tasks will be executed after the scraping is complete.
    # This is achieved by chaining the scraping task with a group of matching tasks.
    
    # Note: The logic to get user IDs and create the group of matching tasks
    # needs to be in a separate task to ensure it runs *after* scraping is done.
    chain(scrape_all_jobs.s(), trigger_matching_for_all_users.s()).apply_async()

@celery_app.task(name="app.tasks.trigger_matching_for_all_users")
def trigger_matching_for_all_users(_):
    """
    This task fetches all active users and creates a parallel matching task for each.
    It's designed to be called after the scraping task is complete.
    """
    logger.info("Scraping finished. Triggering matching for all active users.")
    db = SessionLocal()
    try:
        active_user_ids = db.query(User.id).filter(User.is_active == True).all()
        
        if not active_user_ids:
            logger.info("No active users found. Skipping matching tasks.")
            return

        # Convert UUID objects to strings for Celery serialization
        user_id_strs = [str(user_id[0]) for user_id in active_user_ids]
        
        logger.info(f"Found {len(user_id_strs)} active users. Creating parallel matching tasks.")
        
        # Create a group of tasks to run in parallel
        # This will allow us to match jobs for all active users concurrently
        matching_tasks = group(match_jobs_for_user.s(user_id_str) for user_id_str in user_id_strs)
        matching_tasks.apply_async()
        
        logger.info("Successfully launched all user matching tasks.")

    except Exception as e:
        logger.error(f"Failed to trigger matching tasks: {e}", exc_info=True)
        raise
    finally:
        db.close()
