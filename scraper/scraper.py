import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def scrape_website(url: str) -> str:
    """Scrape content from a website with improved price detection"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
            
        # Specifically look for price-related content
        price_content = []
        
        # Look for price elements (common patterns in e-commerce sites)
        price_selectors = [
            '.price', '#price', '[class*="price"]',  # Generic price classes
            '[class*="product"]', '.product-info',    # Product containers
            '[class*="amount"]', '[class*="cost"]',   # Price amounts
            '.offer', '.sale-price',                  # Special offers
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                price_content.append(element.get_text(strip=True))
        
        # Get main content
        main_content = ' '.join([
            p.get_text(strip=True)
            for p in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3'])
            if p.get_text(strip=True)
        ])
        
        # Combine price-specific content with main content
        all_content = '\n'.join(price_content + [main_content])
        
        # Log the content length for debugging
        logger.info(f"Scraped content length: {len(all_content)} characters")
        logger.debug(f"First 500 characters: {all_content[:500]}")
        
        return all_content

    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return ""