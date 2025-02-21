# Comment out or remove all Celery configuration if you are not using Redis/Celery:
# from celery import Celery
# REDIS_URL = "redis://192.168.112.130:6379/0"
# app = Celery('SearchAI')
# app.conf.update(
#     broker_url=REDIS_URL,
#     result_backend=REDIS_URL,
#     task_serializer='json',
#     result_serializer='json',
#     accept_content=['json'],
#     broker_connection_retry_on_startup=True,
#     task_track_started=True,
#     task_reject_on_worker_lost=True,
#     task_acks_late=True,
#     worker_prefetch_multiplier=1,
#     result_expires=3600,
#     redis_max_connections=None,
#     broker_transport_options={
#         'visibility_timeout': 43200,
#         'socket_timeout': 30,
#         'socket_connect_timeout': 30,
#     }
# )

# from celery import Celery
# from kombu.serialization import register
# import logging
# import sys
# from pathlib import Path
# import json

# Add the project root directory to Python path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration - make sure to use explicit host and port
REDIS_HOST = '192.168.112.130'
REDIS_PORT = '6379'
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

# Create base Celery app
app = Celery('SearchAI')

# Basic config with better error handling
app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    broker_connection_retry_on_startup=True,
    task_track_started=True,
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    redis_max_connections=None,
    broker_transport_options={
        'visibility_timeout': 43200,
        'socket_timeout': 30,
        'socket_connect_timeout': 30,
    }
)

# Load tasks module
app.autodiscover_tasks(['scraper'])
