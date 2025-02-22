from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import time
import logging
from scraper.search_service import get_top_sites
from scraper.scraper import scrape_website
from models.ai_processor import analyze_text
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
uri = "mongodb+srv://mng48301:Falcon695348301%21%26%28@astralcluster.ejzk9.mongodb.net/astral?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['astral']
collection = db['scraped_data']

app = FastAPI() # use to startup: uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

# Basic CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for search progress
search_progress: Dict[str, dict] = {}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

@app.post("/cancel/{search_id}")
async def cancel_search(search_id: str):
    """Cancel an ongoing search"""
    if search_id in search_progress:
        search_progress[search_id].update({
            'status': 'cancelling',
            'cancelled': True,
            'progress': 0
        })
        return {"status": "cancelling"}
    raise HTTPException(status_code=404, detail="Search not found")

@app.get("/search/{search_id}/status")
async def get_search_status(search_id: str):
    """Get the current status of a search"""
    if search_id in search_progress:
        progress = search_progress[search_id]
        return {
            "status": progress.get('status', 'unknown'),
            "progress": progress.get('progress', 0),
            "error": progress.get('error', '')
        }
    raise HTTPException(status_code=404, detail="Search not found")

@app.get("/search/")
async def search(query: str):
    try:
        search_id = str(time.time())
        search_progress[search_id] = {
            'status': 'processing',
            'progress': 0,
            'query': query,
            'cancelled': False
        }
        
        # Update progress: Starting search
        search_progress[search_id]['progress'] = 10
        sites = get_top_sites(query)
        
        if not sites:
            return {
                "status": "failed",
                "error": "No websites found"
            }
            
        # Update progress: Found sites
        search_progress[search_id]['progress'] = 30
        
        # Store scraped content
        detailed_results = []
        
        for idx, url in enumerate(sites[:3]):
            if search_progress[search_id].get('cancelled'):
                return {"status": "cancelled", "search_id": search_id}
                
            try:
                # Update progress: Scraping (30-60%)
                current_progress = 30 + ((idx + 1) * 30 // 3)
                search_progress[search_id]['progress'] = current_progress
                
                content = scrape_website(url)
                if content and len(content.strip()) > 100:
                    detailed_results.append({
                        "url": url,
                        "content": content,
                        "timestamp": time.time()
                    })
                    logger.info(f"Successfully scraped {url}")
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                continue

        if not detailed_results:
            return {
                "status": "failed",
                "error": "Could not extract content from websites"
            }

        # AI Analysis (60-90%)
        search_progress[search_id]['progress'] = 70
        analysis = analyze_text(query, [{"url": r["url"], "content": r["content"]} for r in detailed_results])
        
        # Save complete results to MongoDB
        document = {
            "query": query,
            "sites": [r["url"] for r in detailed_results],
            "summary": analysis.get("summary", "No summary available"),
            "status": "completed",
            "timestamp": time.time(),
            "detailed_results": detailed_results,  # Store full content for each site
            "search_id": search_id
        }
        
        # Insert into MongoDB
        collection.insert_one(document)
        logger.info(f"Stored complete results for query: {query}")
        
        # Return success without the full content
        return {
            "status": "completed",
            "query": query,
            "sites": [r["url"] for r in detailed_results],
            "summary": analysis.get("summary", "No summary available"),
            "search_id": search_id
        }
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "search_id": search_id
        }

@app.get("/data/")
async def get_all_data():
    try:
        data = list(collection.find({}, {'_id': 0}))
        return {"data": data or []}
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return {"data": [], "error": str(e)}

@app.get("/source_detail")
async def get_source_detail(url: str):
    """Return the full text for a single scraped URL."""
    try:
        doc = collection.find_one({"detailedResults.url": url}, {"_id": 0, "detailedResults": 1})
        if not doc:
            raise HTTPException(status_code=404, detail="URL not found")
        
        for item in doc["detailedResults"]:
            if item["url"] == url:
                return {"url": url, "content": item["content"]}
                
        raise HTTPException(status_code=404, detail="Content not found")
    except Exception as e:
        logger.error(f"Error fetching source detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/search/{query}")
async def delete_search(query: str):
    """Delete a search query and its results"""
    try:
        result = collection.delete_one({"query": query})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Search not found")
        return {"status": "success", "message": f"Deleted search: {query}"}
    except Exception as e:
        logger.error(f"Error deleting search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def clean_text_response(text: str) -> str:
    """Clean up text response by removing markdown and JSON formatting"""
    # Remove JSON/markdown formatting patterns
    replacements = {
        '{"type": "markdown", "content": "': '',
        '{"type": "text", "content": "': '',
        '"}': '',
        '**': '',
        '*': '',
        '#': '',
        '\n-': '\n•',  # Replace markdown list markers with bullet points
        '`': ''
    }
    
    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    return cleaned.strip()

@app.post("/ask_context")
async def ask_context(request: dict):
    """Handle context-based questions using Gemini"""
    try:
        # Get the original query and user question
        original_query = request.get("originalQuery")
        user_question = request.get("userQuestion")
        
        if not original_query or not user_question:
            raise HTTPException(status_code=400, detail="Missing query or question")
            
        # Find the stored search results
        stored_data = collection.find_one({"query": original_query})
        if not stored_data:
            raise HTTPException(status_code=404, detail="No data found for this query")
            
        # Format the content for Gemini
        context = "\n\n".join([
            f"Source {i+1}: {result.get('content', 'No content')}"
            for i, result in enumerate(stored_data.get("detailed_results", []))
        ])
        
        # Generate the prompt
        prompt = f"""
        Based on the following content about "{original_query}", 
        please answer this question: "{user_question}"
        
        If the question asks for data visualization, provide the data in a format suitable for Google Charts.
        If numerical analysis is needed, provide structured data.
        
        Context:
        {context}
        
        Provide the response in one of these formats based on the question type:
        1. For visual data: Return type 'graph' with chartType, data, and options
        2. For tabular data: Return type 'table' with headers and rows
        3. For text analysis: Return type 'markdown' with formatted content
        4. For simple answers: Return type 'text' with content
        """
        
        # Get response from Gemini
        response = analyze_text(user_question, [{
            "content": prompt,
            "role": "user"
        }])
        
        if "chart" in user_question.lower() or "graph" in user_question.lower():
            return {
                "type": "graph",
                "graphType": "LineChart",
                "data": response.get("data", []),
                "options": response.get("options", {})
            }
        elif "table" in user_question.lower():
            return {
                "type": "table",
                "headers": response.get("headers", []),
                "data": response.get("data", [])
            }
        else:
            # Clean and format text response
            content = response.get("content", "") or response.get("text", "") or str(response)
            return {
                "type": "text",
                "content": clean_text_response(content)
            }
            
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return {
            "type": "text",
            "content": "Error: Could not process question. Please try rephrasing."
        }
