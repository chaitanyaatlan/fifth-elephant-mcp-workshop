"""
Weather MCP Server

This is the main file that creates an MCP (Model Context Protocol) server 
for weather data. It provides tools that AI assistants can use to get weather information.

MCP servers are like plugins - they give AI assistants new capabilities.
This server adds weather-related tools.
"""

# Standard library imports
import sys
import logging
from typing import Dict, Any

# MCP (Model Context Protocol) library
from mcp.server.fastmcp import FastMCP

# Our custom modules
from apis import get_location_coordinates, get_current_weather_from_api, get_forecast_from_api
from utils import validate_api_key, format_current_weather_response, format_forecast_response, validate_forecast_days

# Debug message for Claude Desktop (helps with troubleshooting)
print("🚀 Weather MCP Server Starting...", file=sys.stderr, flush=True)

# Set up logging (for debugging and monitoring)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("📦 Modules loaded successfully", file=sys.stderr, flush=True)

# Create the MCP server instance
# This is what handles communication between AI assistants and our tools
mcp = FastMCP("weather-mcp")


@mcp.tool("get_current_weather")
async def get_current_weather(location: str) -> Dict[str, Any]:
    """
    Get current weather conditions for any city worldwide.
    
    This tool provides real-time weather data including temperature, humidity, 
    wind speed, and weather conditions. Perfect for checking current weather
    before going out or planning activities.
    
    Args:
        location (str): City name, optionally with state/country codes.
                       Examples: "London", "New York,US", "Tokyo,JP", "Paris,FR"
    
    Returns:
        Dict containing:
        - location: city name, country, coordinates
        - temperature: current, feels-like, min/max temperatures in Celsius
        - weather_condition: main condition (sunny, cloudy, etc.) and description
        - wind: speed (m/s) and direction (degrees)
        - atmosphere: humidity (%), pressure (hPa), visibility (m), cloudiness (%)
        - sun: sunrise and sunset times
        - timestamp: when this data was recorded
    
    Example usage:
        - "What's the weather like in London?"
        - "How warm is it in Miami right now?"
        - "Is it raining in Seattle?"
    """
    # Step 1: Check if API key is configured
    error_msg = validate_api_key()
    if error_msg:
        return {"error": error_msg}
    
    try:
        # Step 2: Convert city name to coordinates (latitude/longitude)
        success, location_data = get_location_coordinates(location)
        if not success:
            return {"error": location_data}
        
        # Step 3: Get weather data for those coordinates
        success, weather_data = get_current_weather_from_api(
            location_data["lat"], location_data["lon"]
        )
        if not success:
            return {"error": weather_data}
        
        # Step 4: Format the data nicely and return it
        return format_current_weather_response(weather_data, location_data)
        
    except Exception as e:
        # Log the error and return a user-friendly message
        logger.error(f"Error getting current weather for {location}: {str(e)}")
        return {"error": f"Failed to fetch current weather: {str(e)}"}


@mcp.tool("get_weather_forecast")
async def get_weather_forecast(location: str, days: int = 5) -> Dict[str, Any]:
    """
    Get weather forecast for the next 1-5 days for any city worldwide.
    
    This tool provides detailed weather predictions including temperature trends,
    precipitation chances, and weather conditions for planning ahead. Data is 
    provided in 3-hour intervals for accuracy.
    
    Args:
        location (str): City name, optionally with state/country codes.
                       Examples: "London", "New York,US", "Tokyo,JP", "Paris,FR"
        days (int): Number of days to forecast (1-5). Defaults to 5 days.
                   More days = more detailed planning information.
    
    Returns:
        Dict containing:
        - location: city name, country, coordinates
        - forecast: list of weather predictions (every 3 hours)
          Each forecast includes:
          - datetime: when this forecast is for
          - temperature: temp, feels-like, min/max in Celsius
          - weather_condition: main condition and detailed description
          - wind: speed and direction
          - atmosphere: humidity, pressure, cloudiness, visibility
          - precipitation_probability: chance of rain/snow (0-100%)
        - days_requested: how many days you asked for
        - total_forecasts: total number of 3-hour periods included
    
    Example usage:
        - "What will the weather be like in Paris this week?"
        - "Should I bring an umbrella to London tomorrow?"
        - "Will it be sunny in Miami this weekend?"
    """
    # Step 1: Check if API key is configured
    error_msg = validate_api_key()
    if error_msg:
        return {"error": error_msg}
    
    # Step 2: Make sure days is between 1 and 5 (API limitation)
    days = validate_forecast_days(days)
    
    try:
        # Step 3: Convert city name to coordinates
        success, location_data = get_location_coordinates(location)
        if not success:
            return {"error": location_data}
        
        # Step 4: Get forecast data for those coordinates
        success, forecast_data = get_forecast_from_api(
            location_data["lat"], location_data["lon"], days
        )
        if not success:
            return {"error": forecast_data}
        
        # Step 5: Format the forecast data nicely and return it
        return format_forecast_response(forecast_data, location_data, days)
        
    except Exception as e:
        # Log the error and return a user-friendly message
        logger.error(f"Error getting forecast for {location}: {str(e)}")
        return {"error": f"Failed to fetch weather forecast: {str(e)}"}


# This block runs when the script is executed directly (not imported)
if __name__ == "__main__":
    # Print startup status
    logger.info("🌤️  Weather MCP Server ready!")
    
    # Start the MCP server
    # This makes the server listen for requests from AI assistants
    mcp.run()