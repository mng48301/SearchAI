import logging
from scraper.search_service import get_top_sites
from scraper.scraper import scrape_website
from models.ai_processor import analyze_text
from datetime import datetime

logger = logging.getLogger(__name__)

async def process_search(query: str):
    """Process a search query and return results"""
    try:
        # Get search results using Selenium
        sites = get_top_sites(query)
        if not sites:
            return {"status": "failed", "error": "No websites found"}

        # Scrape content from sites
        results = []
        for url in sites[:3]:
            try:
                content = scrape_website(url)
                if content:
                    results.append({
                        "url": url,
                        "content": content,
                        "timestamp": datetime.now()
                    })
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                continue

        if not results:
            return {"status": "failed", "error": "Could not extract content"}

        # Process with AI
        analysis = analyze_text(query, results)
        
        return {
            "status": "completed",
            "query": query,
            "sites": [r["url"] for r in results],
            "summary": analysis.get("summary", "No summary available"),
            "timestamp": datetime.now(),
            "detailed_results": results
        }

    except Exception as e:
        logger.error(f"Search processing failed: {str(e)}")
        return {"status": "failed", "error": str(e)}
