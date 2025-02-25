import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def scrape_website(url: str) -> str:
    """Scrapes content from a website using requests instead of Selenium"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'iframe', 'header']):
            tag.decompose()
        
        # Get main content with prioritized selectors
        main_content = ''
        priority_selectors = [
            'main', 'article', '#main-content', '.main-content',
            '[role="main"]', '.content', '#content'
        ]
        
        # Try priority selectors first
        for selector in priority_selectors:
            content = soup.select_one(selector)
            if content:
                main_content = content.get_text(separator=' ', strip=True)
                break
        
        # If no content found, get all paragraphs
        if not main_content:
            paragraphs = []
            for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
                text = p.get_text(strip=True)
                if len(text) > 20:  # Only include substantial paragraphs
                    paragraphs.append(text)
            main_content = ' '.join(paragraphs)
        
        # Log content length for debugging
        logger.info(f"Successfully scraped {url} - Content length: {len(main_content)}")
        return main_content

    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return ""
