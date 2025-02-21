import os
import sys
from pathlib import Path

# Add project root to Python path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

# Import and run celery worker
from config import app

if __name__ == '__main__':
    app.worker_main(['worker', '--loglevel=info', '-Q', 'scraper', '--pool=solo'])
