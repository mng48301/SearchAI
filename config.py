from decouple import config

# API Keys
GEMINI_API_KEY = config('GEMINI_API_KEY')

# MongoDB settings
MONGODB_URI = config('MONGODB_URI', default="mongodb+srv://mng48301:Falcon695348301%21%26%28@astralcluster.ejzk9.mongodb.net/astral")
MONGODB_DB = config('MONGODB_DB', default="astral")
MONGODB_COLLECTION = config('MONGODB_COLLECTION', default="scraped_data")

# API settings
API_HOST = config('API_HOST', default='127.0.0.1')  # Changed from 0.0.0.0
API_PORT = config('API_PORT', default=8000)
