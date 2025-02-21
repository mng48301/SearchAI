# main.py or app.py
from tasks import scrape_task

# Example URL list
urls = ['https://www.amazon.com/', 'https://www.aliexpress.us']

for url in urls:
    scrape_task.delay(url)
