import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def clean_summary(text: str) -> str:
    """Remove markdown formatting from summary"""
    return text.replace('*', '').replace('#', '').strip()

def analyze_text(query: str, sources: list) -> dict:
    """Generate a comprehensive summary of all scraped content"""
    try:
        # Combine all source content for analysis
        combined_text = ""
        for idx, source in enumerate(sources, 1):
            combined_text += f"\nSource {idx} ({source['url']}):\n{source['content'][:2000]}\n"

        prompt = f"""
        Based on the search query: "{query}"
        
        Analyze the following content from {len(sources)} different sources and provide:
        1. A comprehensive summary (3-4 sentences)
        2. Key points or findings
        3. Any relevant data, prices, or statistics found
        
        Content to analyze:
        {combined_text}
        
        Format the response clearly with main points and findings.
        """

        response = model.generate_content(prompt)
        
        if not response.text:
            raise ValueError("No summary generated")
            
        summary = clean_summary(response.text)
        return {
            "summary": summary,
            "sources": [s['url'] for s in sources],
            "query": query
        }

    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return {
            "summary": f"Error generating summary: {str(e)}",
            "sources": [s['url'] for s in sources],
            "query": query
        }
