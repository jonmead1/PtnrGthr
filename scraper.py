from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin

from config import RETRY_DELAY, MAX_RETRIES, PARTNER_KEYWORDS, PARTNER_NAME_PATTERNS
from url_processor import URLProcessor

logger = logging.getLogger(__name__)

class PartnerProgramScraper:
    def __init__(self):
        self.driver = None
        self.visited_urls = set()

    def __enter__(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')

            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            return self

        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def _extract_text_content(self) -> str:
        """Extract text content from the current page."""
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text
        except Exception as e:
            logger.error(f"Error extracting text content: {str(e)}")
            return ""

    def _find_partner_links(self) -> List[str]:
        """Find links that might lead to partner program pages."""
        partner_links = []
        try:
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            for element in elements:
                try:
                    href = element.get_attribute("href")
                    text = element.text.lower()
                    if href and any(keyword in text for keyword in PARTNER_KEYWORDS):
                        if href not in self.visited_urls:  # Only add unvisited URLs
                            partner_links.append(href)
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Error finding partner links: {str(e)}")
        return list(set(partner_links))

    def _extract_partner_names(self) -> List[str]:
        """Extract partner company names from the page."""
        partner_names = []
        try:
            # Look for partner names in lists
            for tag in ['ul', 'ol']:
                lists = self.driver.find_elements(By.TAG_NAME, tag)
                for list_elem in lists:
                    items = list_elem.find_elements(By.TAG_NAME, 'li')
                    for item in items:
                        text = item.text.strip()
                        if text and len(text) > 3 and any(word in text.lower() for word in PARTNER_NAME_PATTERNS):
                            partner_names.append(text)

            # Look for partner names in headings and paragraphs
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 3 and any(word in text.lower() for word in PARTNER_NAME_PATTERNS):
                        partner_names.append(text)

        except Exception as e:
            logger.error(f"Error extracting partner names: {str(e)}")

        return list(set(partner_names))

    def _extract_program_types(self, text: str) -> List[str]:
        """Extract different types of partner programs mentioned."""
        program_types = []
        for keyword in PARTNER_KEYWORDS:
            if keyword in text.lower():
                program_types.append(keyword)
        return list(set(program_types))

    def _extract_page_structure(self) -> str:
        """Analyze the page structure."""
        try:
            has_form = bool(self.driver.find_elements(By.TAG_NAME, "form"))
            has_contact = "contact" in self._extract_text_content().lower()
            has_pricing = "pricing" in self._extract_text_content().lower()

            if has_form:
                return "registration_form"
            elif has_contact:
                return "contact_page"
            elif has_pricing:
                return "pricing_page"
            else:
                return "information_page"
        except Exception as e:
            logger.error(f"Error analyzing page structure: {str(e)}")
            return "unknown"

    def _process_subpage(self, url: str) -> Dict:
        """Process a single sub-page and extract information."""
        subpage_result = {
            'url': url,
            'program_types': [],
            'partner_names': [],
            'page_structure': 'unknown'
        }

        try:
            if url in self.visited_urls:
                return subpage_result

            self.visited_urls.add(url)
            self.driver.get(url)

            # Wait for body to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Extract information
            text_content = self._extract_text_content()
            subpage_result['program_types'] = self._extract_program_types(text_content)
            subpage_result['partner_names'] = self._extract_partner_names()
            subpage_result['page_structure'] = self._extract_page_structure()

        except Exception as e:
            logger.error(f"Error processing sub-page {url}: {str(e)}")

        return subpage_result

    def scrape_url(self, url: str) -> Dict:
        """Main method to scrape a single URL and its partner-related sub-pages."""
        result = {
            'domain': URLProcessor.get_base_domain(url),
            'partner_program_url': '',
            'url_path': '',
            'program_types': [],
            'partner_names': [],
            'page_structure': 'unknown',
            'status': 'pending',
            'subpages': []
        }

        try:
            normalized_url = URLProcessor.normalize_url(url)
            logger.info(f"Navigating to URL: {normalized_url}")

            # Process main page
            main_page_info = self._process_subpage(normalized_url)
            result.update({
                'partner_program_url': normalized_url,
                'program_types': main_page_info['program_types'],
                'partner_names': main_page_info['partner_names'],
                'page_structure': main_page_info['page_structure']
            })

            # Find and process partner-related sub-pages
            partner_links = self._find_partner_links()
            for link in partner_links:
                if URLProcessor.is_same_domain(url, link):
                    subpage_info = self._process_subpage(link)
                    if subpage_info['program_types'] or subpage_info['partner_names']:
                        result['subpages'].append(subpage_info)
                        # Merge unique program types and partner names
                        result['program_types'] = list(set(result['program_types'] + subpage_info['program_types']))
                        result['partner_names'] = list(set(result['partner_names'] + subpage_info['partner_names']))

            result['status'] = 'success'

        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            result['status'] = f'error: {str(e)}'

        return result
