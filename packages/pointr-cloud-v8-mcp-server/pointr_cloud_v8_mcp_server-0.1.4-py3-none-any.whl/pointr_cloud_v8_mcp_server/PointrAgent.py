from agents import Agent, Runner, trace
from dotenv import load_dotenv
from fastmcp import FastMCP
import os
import logging


# Set up logging to a file
logging.basicConfig(
    filename="pointr_agent.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
load_dotenv(override=True)

mcp = FastMCP("Pointr Cloud MCP Server")

SYSTEM_PROMPT = """
You are a helpful assistant that can guide users to find their ways by providing them QR code links. 
Your task is to first understand where the user wants to go and extract the exact location by asking additional questions 
or if user is not too specific you can provide a QR code for a speecific category of place based on user feedback 
such as toilets/restaurants or entertaintment. Do not ask additional questions if user does not give you details. To provide the QR code, you can use the Pointr API to generate a QR code link for the specific location.
Do not ask user where they are, just create the QR Code. Do not use any other APIs or services to generate the QR code, just use the Pointr API.
As a response also mention if QR code is for category or specific place.
"""



@mcp.tool()
def find_exact_poi_from_user_input(userinput: str):
    """ Find the exact point of interest (POI) ID from user input. 
    If user is specific like giving the name of the place or name of the meeting room or name of the restaurant 
    this function should be used.  
    Args:
        userinput (str): The user input containing the point of interest."""
    poi="23123123213213123212312321321312321321"  # Simulated POI extraction logic
    return {"status": "success", "poiId": poi}


@mcp.tool()
def find_exact_category_from_user_input(userinput: str):
    """ Find the exact category from user input. If user input is not specific enough,
    it will return a general category such as 'toilets', 'restaurants', or 'entertainment'. 
    This category text should be a noun and singular. 
    Args:
        userinput (str): The user input containing the category"""
    userinput_lower = userinput.lower()
    if "cafe" in userinput_lower or "coffee" in userinput_lower:
        category = "Cafe"
    elif "restaurant" in userinput_lower:
        category = "Restaurant"
    elif "toilet" in userinput_lower or "restroom" in userinput_lower or "bathroom" in userinput_lower:
        category = "Restroom"
    elif "entertainment" in userinput_lower:
        category = "Entertainment"
    else:
        # Default fallback or echo the input as category
        category = userinput.capitalize()

    logging.info(f"Client Identifier: {os.getenv('PC_CLIENT_ID')}")
    return {"status": "success", "category": category}

@mcp.tool()
def generate_qr_code_for_specific_poi(poi: str):
    """ Generate a QR code for a specific point of interest (POI) 
    Args:
        poi (str): The point of interest for which to generate the QR code."""
    logging.info(f"Client Identifier: {os.getenv('PC_CLIENT_ID')}")
    return {"status": "success", "qr_code": f"https://example.com/qr/{poi}"}

@mcp.tool()
def generate_qr_code_for_category(category: str):
    """ Generate a QR code for a category of points of interest (POI).
    This function is used when the user is not specific about the exact location but mentions a category
    such as 'toilets', 'restaurants', or 'entertainment'.
    Args:
        category (str): The category for which to generate the QR code."""
    logging.info(f"Client Identifier: {os.getenv('PC_CLIENT_ID')}")
    return {"status": "success", "qr_code": f"https://example.com/qr/category/{category}"}


def main(transport='stdio'):
    # ...existing setup...
    if transport == "http":
        #mcp.run(transport='streamable-http')
        mcp.run(transport="http",
                host="127.0.0.1",
                port=4200,
                log_level="debug")
    else:
        mcp.run(transport='stdio')

