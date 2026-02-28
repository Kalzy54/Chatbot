import logging
import time
import warnings
from typing import Set, List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# Suppress XML parsing warnings
try:
    from bs4 import XMLParsedAsHTMLWarning
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
except Exception:
    pass

logger = logging.getLogger(__name__)


class UniversityWebScraper:
    def __init__(self, base_url: str, max_pages: int = 50, delay_seconds: float = 0.5):
        """
        Initialize web scraper for library or university website.
        
        Args:
            base_url: Starting URL (e.g., https://library.university.edu/ or https://miu.edu.ng/)
            max_pages: Maximum pages to crawl
            delay_seconds: Delay between requests (be respectful)
        """
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.delay_seconds = delay_seconds
        self.visited: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LibraryChat-Bot/1.0 (Educational & Research Purpose)'
        })

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to the domain and is not a duplicate."""
        parsed = urlparse(url)
        # Only crawl same domain
        if parsed.netloc != self.domain:
            return False
        # Avoid duplicates and fragments
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if clean_url in self.visited:
            return False
        
        # Skip common non-content URLs and malformed patterns
        skip_patterns = [
            '.pdf', '.jpg', '.png', '.gif', '.zip', '.exe',
            'javascript:', '#', 'mailto:', 'tel:',
            'mail.miu.edu.ng', 'mewaruniversitynigeria', 'miunigeria',  # malformed links
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',  # social media
            '/search', '/login', '/admin', '?', '&'  # utility pages
        ]
        url_lower = url.lower()
        if any(pattern in url_lower for pattern in skip_patterns):
            return False
        
        return True

    def _extract_text_from_html(self, html: str) -> str:
        """Extract clean text from HTML."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            soup = BeautifulSoup(html, 'html.parser')
        # Remove script and style
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

    def fetch_page(self, url: str) -> str:
        """Fetch and extract text from a single page."""
        if url in self.visited:
            return ""
        
        self.visited.add(url)
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return self._extract_text_from_html(response.content)
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return ""

    def crawl(self) -> List[str]:
        """
        Crawl the website and return list of text chunks.
        """
        pages_crawled = 0
        to_visit = [self.base_url]
        all_text = []

        while to_visit and pages_crawled < self.max_pages:
            url = to_visit.pop(0)
            
            if not self._is_valid_url(url):
                continue

            text = self.fetch_page(url)
            if text:
                all_text.append(text)
                pages_crawled += 1

            # Extract links from the page
            try:
                response = self.session.get(url, timeout=10)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    soup = BeautifulSoup(response.content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href'].strip()
                    if not href or href.startswith('#'):
                        continue
                    absolute_url = urljoin(url, href)
                    if self._is_valid_url(absolute_url):
                        to_visit.append(absolute_url)
            except Exception as e:
                logger.debug(f"Error extracting links from {url}: {e}")

            # Be respectful: add delay between requests
            time.sleep(self.delay_seconds)

        logger.info(f"Crawled {pages_crawled} pages from {self.base_url}")
        return all_text
