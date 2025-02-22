import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
import json

logger = logging.getLogger(__name__)

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def format_graph_data(response_text: str) -> dict:
    """Format response data for Google Charts"""
    try:
        # Default chart configuration
        chart_data = {
            "type": "graph",
            "graphType": "LineChart",
            "title": "Data Visualization",
            "data": [
                ["X", "Y"],  # Default headers
                ["No Data", 0]  # Default data point
            ],
            "options": {
                "title": "Data Visualization",
                "hAxis": {"title": "Category"},
                "vAxis": {"title": "Value"},
                "curveType": "function",
                "legend": {"position": "bottom"}
            }
        }
        
        # Try to extract numerical data from the text
        import re
        numbers = re.findall(r'(\d+(?:\.\d+)?)', response_text)
        labels = re.findall(r'([A-Za-z]+(?:\s[A-Za-z]+)*)\s*:\s*\d+', response_text)
        
        if numbers and labels:
            chart_data["data"] = [
                ["Category", "Value"]  # Headers
            ] + list(zip(labels, map(float, numbers[:len(labels)])))
            
            # Update chart title if found
            title_match = re.search(r'title["\s:]+([^"}\n]+)', response_text, re.I)
            if title_match:
                chart_data["title"] = title_match.group(1).strip()
                chart_data["options"]["title"] = chart_data["title"]
        
        return chart_data
        
    except Exception as e:
        logger.error(f"Error formatting graph data: {e}")
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

def analyze_text(question: str, sources: list) -> dict:
    """Generate analysis of content based on the question"""
    try:
        if not sources or not isinstance(sources, list):
            raise ValueError("Invalid sources provided")

        # Format content for analysis
        formatted_content = ""
        if isinstance(sources[0], dict) and 'content' in sources[0]:
            # Handle content from direct API call
            formatted_content = sources[0]['content']
        else:
            # Handle content from database
            formatted_content = "\n\n".join([
                f"Source {i+1}: {source.get('content', '')}"
                for i, source in enumerate(sources)
            ])

        # Detect if visualization is needed
        needs_visualization = any(word in question.lower() 
                               for word in ['graph', 'chart', 'plot', 'visualize', 'compare', 'trend'])

        if "price" in question.lower() or "cost" in question.lower():
            prompt = f"""
            Extract price information from this content and create a price comparison.
            List each item and its price clearly in this format:
            ItemName: $price
            
            Question: {question}
            Content: {formatted_content}
            """
            
            response = model.generate_content(prompt)
            graph_data = format_price_data(response.text)
            
            if graph_data and len(graph_data["data"]) > 1:
                return graph_data
            
            # Fallback to regular text if no price data found
            return {
                "type": "text",
                "content": "Could not find price information to compare. " + response.text
            }

        if needs_visualization:
            prompt = f"""
            Analyze this content and answer: "{question}"
            Create a data visualization using this content.
            
            Return your response in this JSON format:
            {{
                "type": "graph",
                "graphType": "LineChart/BarChart/PieChart",
                "title": "Chart title",
                "data": [["Header1", "Header2"], [value1, value2], ...],
                "options": {{
                    "title": "Chart title",
                    "hAxis": {{"title": "X-axis label"}},
                    "vAxis": {{"title": "Y-axis label"}}
                }}
            }}

            Content to analyze:
            {formatted_content}
            """
        else:
            prompt = f"""
            Based on this content, answer: "{question}"
            
            Content to analyze:
            {formatted_content}
            
            Provide a clear, structured response.
            """

        response = model.generate_content(prompt)
        
        if not response.text:
            raise ValueError("No response generated")

        # Handle visualization requests
        if any(word in question.lower() for word in ['graph', 'chart', 'plot', 'visualize', 'compare', 'trend']):
            graph_data = format_graph_data(response.text)
            if graph_data:
                return graph_data

        # Handle table requests
        if any(word in question.lower() for word in ['table', 'compare', 'list']):
            # Format as table with at least headers and one row
            return {
                "type": "table",
                "headers": ["Category", "Value"],
                "data": [["Sample", "Data"]],
                "title": "Data Table"
            }

        # Default to markdown
        return {
            "type": "markdown",
            "content": response.text
        }

    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}")
        return {
            "type": "markdown",
            "content": f"Error analyzing content: {str(e)}"
        }
