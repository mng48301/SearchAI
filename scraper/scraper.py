import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def scrape_website(url: str) -> str:
    """Simple scraper that extracts main text content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        content = ' '.join(lines)
        
        logger.info(f"Scraped {len(content)} chars from {url}")
        return content

    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return ""
