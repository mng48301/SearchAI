import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

logger = logging.getLogger(__name__)

def get_top_sites(query: str, num_results: int = 3) -> list:
    """Get top search results using undetected-chromedriver"""
    driver = None
    try:
        logger.info(f"Searching for: {query}")
        
        options = uc.ChromeOptions()
        options.add_argument('--disable-dev-shm-usage')
        options.headless = False
        
        driver = uc.Chrome(options=options)
        driver.get("https://www.google.com")
        
        # Wait for search box and handle cookie consent if present
        wait = WebDriverWait(driver, 10)

        try:
            consent_button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Accept all')]"))
            )
            consent_button.click()
            time.sleep(1)
        except:
            logger.info("No consent button found")
            
        # Find and interact with search box
        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        
        # Wait for search results to load
        wait.until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        time.sleep(3)  # Wait longer for results
        
        results = []
        # First try: main search results
        main_results = driver.find_elements(By.CSS_SELECTOR, "div.g div.yuRUbf > a")
        
        # Second try: broader search
        if len(main_results) < num_results:
            main_results.extend(driver.find_elements(By.CSS_SELECTOR, "div.g > div > div > div > a"))
            
        # Process all found elements
        for element in main_results:
            if len(results) >= num_results:
                break
                
            try:
                url = element.get_attribute('href')
                if url and url.startswith('http') and not any(x in url.lower() for x in [
                    'google.', 'youtube.', 'facebook.', 'linkedin.', 'twitter.'
                ]):
                    if url not in results:  # Avoid duplicates
                        results.append(url)
                        logger.info(f"Found URL: {url}")
            except Exception as e:
                logger.error(f"Error extracting URL: {str(e)}")
                continue

        # If we still don't have enough results, try another method
        if len(results) < num_results:
            logger.info("Trying alternate method...")
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                if len(results) >= num_results:
                    break
                try:
                    url = link.get_attribute('href')
                    if (url and 
                        url.startswith('http') and 
                        not any(x in url.lower() for x in ['google.', 'youtube.', 'facebook.']) and
                        url not in results):
                        results.append(url)
                        logger.info(f"Found URL (alternate): {url}")
                except:
                    continue

        if not results:
            logger.error("No results found")
        else:
            logger.info(f"Found {len(results)} results: {results}")
            
        return results[:num_results]

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        return []
        
    finally:
        if driver:
            time.sleep(1)
            try:
                driver.quit()
            except:
                pass