from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from pathlib import Path
from dotenv import load_dotenv
import os
# MongoDB Atlas URI
load_dotenv()
client = MongoClient(os.getenv('MONGODB_API_KEY'))
db = client['astral']
collection = db['scraped_data']

app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Dynamically reference the static directory
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/")
def read_root(request: Request):
    data = list(collection.find())
    return templates.TemplateResponse("index.html", {"request": request, "data": data})