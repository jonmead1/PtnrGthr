from urllib.parse import urljoin, urlparse
from typing import List, Set
import logging

logger = logging.getLogger(__name__)

class URLProcessor:
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL by adding https:// if missing."""
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    @staticmethod
    def get_base_domain(url: str) -> str:
        """Extract base domain from URL."""
        parsed = urlparse(URLProcessor.normalize_url(url))
        return parsed.netloc

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception as e:
            logger.error(f"Error validating URL {url}: {str(e)}")
            return False

    @staticmethod
    def is_same_domain(url1: str, url2: str) -> bool:
        """Check if two URLs belong to the same domain."""
        domain1 = URLProcessor.get_base_domain(url1)
        domain2 = URLProcessor.get_base_domain(url2)
        return domain1 == domain2

    @staticmethod
    def build_absolute_url(base_url: str, relative_url: str) -> str:
        """Convert relative URL to absolute URL."""
        try:
            return urljoin(base_url, relative_url)
        except Exception as e:
            logger.error(f"Error building absolute URL from {base_url} and {relative_url}: {str(e)}")
            return ""

    @staticmethod
    def clean_url(url: str) -> str:
        """Clean URL by removing fragments and query parameters."""
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except Exception as e:
            logger.error(f"Error cleaning URL {url}: {str(e)}")
            return url
