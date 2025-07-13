import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract base class for job scrapers.
    Defines the interface for fetching and normalizing job data from a source.
    """

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Returns the unique name of the data source.
        e.g., 'remoteok', 'arbeitnow'
        """
        pass

    @abstractmethod
    def fetch_and_normalize(self) -> List[Dict[str, Any]]:
        """
        Fetches raw data from the source API and normalizes it into a list
        of standardized dictionaries.
        """
        pass

    def _make_request(self, url: str) -> Optional[Any]:
        """
        A helper method to perform a GET request and handle common errors.
        """
        try:
            # Using httpx for modern, async-capable HTTP requests
            with httpx.Client() as client:
                response = client.get(url, timeout=30.0, follow_redirects=True)
                response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"Network request failed for {self.get_source_name()}: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {self.get_source_name()}: {e.response.status_code}")
        except Exception as e:
            logger.error(f"An unexpected error occurred when fetching from {self.get_source_name()}: {e}")
        
        return None
