import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
import json

logger = logging.getLogger(__name__)

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def format_graph_data(text: str) -> dict:
    """Extract and format data for visualization"""
    try:
        # Extract numbers and labels from text
        import re
        numbers = re.findall(r'\$?(\d+(?:\.\d+)?)', text)
        labels = re.findall(r'([A-Za-z\s]+?):\s*\$?\d+', text)
        
        if not numbers or not labels:
            return None
            
        return {
            "type": "graph",
            "graphType": "BarChart",
            "data": [
                ["Item", "Price ($)"],  # Clear headers
                *[(label.strip(), float(price)) for label, price in zip(labels, numbers)]
            ],
            "options": {
                "title": "Price Comparison",
                "hAxis": {"title": "Items"},
                "vAxis": {"title": "Price ($)"},
                "legend": "none"
            }
        }
    except:
        return None

def format_price_data(text: str) -> dict:
    """Extract and format price data for visualization"""
    import re
    
    # Find price patterns (e.g., $123.45, 123.45, 123)
    price_pattern = r'\$?\s*(\d+(?:\.\d{2})?)'
    prices = re.findall(price_pattern, text)
    
    # Find associated product/item names
    # Look for words before prices or between colons and prices
    name_pattern = r'([A-Za-z0-9\s\-]+?)(?:\s*:|\s+\$?\s*\d+\.?\d*)'
    names = re.findall(name_pattern, text)
    
    if prices and names:
        return {
            "type": "graph",
            "graphType": "BarChart",  # Better for price comparisons
            "data": [
                ["Product", "Price ($)"],  # Clear headers
                *list(zip(
                    [name.strip() for name in names[:len(prices)]], 
                    [float(price) for price in prices[:len(names)]] 
                ))
            ],
            "options": {
                "title": "Price Comparison",
                "hAxis": {"title": "Products"},
                "vAxis": {"title": "Price ($)"},
                "legend": {"position": "none"},
                "bars": {"groupWidth": "75%"},
            }
        }
    
    return None

def format_table_data(text: str) -> dict:
    """Convert text-based table data into structured format"""
    try:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) < 2:  # Need at least header and one row
            return None
            
        # Try to detect table structure
        if '|' in lines[0]:  # Markdown table
            rows = [
                [cell.strip() for cell in line.split('|') if cell.strip()]
                for line in lines if not line.startswith('|-')
            ]
        else:  # Space/colon separated
            rows = [line.split(':') if ':' in line else line.split()
                   for line in lines]
        
        if not rows:
            return None
            
        return {
            "type": "table",
            "headers": rows[0],
            "rows": rows[1:],
            "options": {
                "showRowNumber": True,
                "width": "100%",
                "pageSize": 10
            }
        }
    except:
        return None

def analyze_text(question: str, sources: list) -> dict:
    """Generate analysis of content based on the question"""
    try:
        if not sources:
            return {"content": "No source content available for analysis"}

        # Format content with source information
        formatted_content = "\n\n".join([
            f"Source ({source['url']}):\n{source['content']}"
            for source in sources
        ])
        
        # Log for debugging
        logger.debug(f"Processing question: {question}")
        logger.debug(f"Number of sources: {len(sources)}")
        
        # Determine query type and create appropriate prompt
        question_lower = question.lower()
        is_summary = 'summary' in question_lower or 'summarize' in question_lower
        is_price_related = any(word in question_lower for word in ['price', 'cost', 'deal', '$'])
        needs_visualization = any(word in question_lower for word in ['graph', 'chart', 'plot', 'visualize'])
        needs_table = any(word in question_lower for word in ['table', 'list', 'compare', 'breakdown'])

        if is_summary:
            prompt = f"""
            Provide a concise summary of this content. Include key points and main findings.
            
            Content to summarize:
            {formatted_content}
            """
        elif is_price_related:
            prompt = f"""
            Extract price information from this content:
            - List all products and their prices
            - Include any deals or discounts mentioned
            - Format prices as "Product: $XX.XX"
            
            Content to analyze:
            {formatted_content}
            
            Question: {question}
            """
        elif needs_table:
            prompt = f"""
            Extract and organize the information into a table format.
            Present your response as a table with clear headers and rows.
            Format using either:
            1. Column1 | Column2 | Column3
            2. Item: Value format
            
            Question: {question}
            Content: {formatted_content}
            """
            
            response = model.generate_content(prompt)
            
            if not response.text:
                return {"content": "No response generated"}
                
            table_data = format_table_data(response.text)
            if table_data:
                return table_data
        else:
            prompt = f"""
            Answer this question using the provided content: {question}
            
            Content to analyze:
            {formatted_content}
            
            Provide a clear, direct response.
            """

        response = model.generate_content(prompt)
        
        if not response.text:
            return {"content": "No response generated"}

        # Handle visualization if needed
        if needs_visualization and is_price_related:
            graph_data = format_price_data(response.text)
            if graph_data:
                return graph_data

        # Return clean text response
        return {
            "type": "text",
            "content": response.text.strip()
        }

    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}")
        return {"content": f"Error analyzing content: {str(e)}"}