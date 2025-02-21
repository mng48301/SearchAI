from celery import shared_task, states
from celery.exceptions import Ignore
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def search_task(self, query):
    """Search task for finding and analyzing content"""
    logger.info(f"Starting search task for query: {query}")
    
    try:
        # Simulate work
        result = {
            "status": states.SUCCESS,
            "query": query,
            "sites": ["https://example.com"],
            "content": "Test content"
        }
        
        self.update_state(
            state=states.SUCCESS,
            meta=result
        )
        return result
        
    except Exception as exc:
        logger.exception("Task failed")
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(exc).__name__,
                'exc_message': str(exc),
                'status': states.FAILURE
            }
        )
        raise Ignore()

@shared_task(bind=True)
def scrape_task(self, url):
    """Legacy scrape task"""
    logger.info(f"Starting scrape task for URL: {url}")
    
    try:
        result = {
            "status": states.SUCCESS,
            "url": url,
            "content": "Test content"
        }
        return result
        
    except Exception as exc:
        logger.exception("Task failed")
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(exc).__name__,
                'exc_message': str(exc),
                'status': states.FAILURE
            }
        )
        raise Ignore()
