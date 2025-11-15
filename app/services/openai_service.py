import openai
import logging
from functools import lru_cache
from app.core.config import settings

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_openai_client() -> openai.OpenAI:
    """
    Initializes and returns the OpenAI client.
    It uses the OPENAI_API_KEY from the unified config.
    The client is cached to avoid re-initialization on every call.
    """
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        logger.error("OPENAI_API_KEY not set in configuration.")
        raise ValueError("OPENAI_API_KEY not set in configuration.")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        # Test the client by making a simple call
        client.models.list()
        logger.info("OpenAI client initialized successfully.")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        raise
