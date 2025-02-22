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
