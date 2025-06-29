"""
Weather API Functions

This file contains all functions that interact with the OpenWeather API.
It handles making HTTP requests and getting data from different endpoints.
"""

import requests
import os
from typing import Any, Dict, Tuple
from dotenv import load_dotenv

# Load environment variables (like API keys)
load_dotenv()

# API configuration
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"  # Main weather API
GEO_URL = "https://api.openweathermap.org/geo/1.0"    # Location search API


def make_api_request(url: str) -> Tuple[bool, Any]:
    """
    Make a request to any API endpoint and handle common errors.
    
    This is our "global fetch function" that handles all API calls in one place.
    
    Args:
        url (str): The complete API URL to call
        
    Returns:
        Tuple of (success: bool, data: dict or error_message: str)
        - If success=True: data contains the API response
        - If success=False: data contains the error message
    """
    try:
        # Make the HTTP request with a 10-second timeout
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Check if API returned an authentication error
        if isinstance(data, dict) and data.get('cod') in [401, '401']:
            return False, f"API Key error: {data.get('message', 'Invalid API key')}"
        
        # Check if API returned any other error
        if response.status_code != 200:
            return False, f"API error: {data.get('message', 'Unknown error')}"
            
        # Success! Return the data
        return True, data
        
    except requests.exceptions.Timeout:
        return False, "Request timeout - please try again"
    except requests.exceptions.RequestException as e:
        return False, f"Network error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def get_location_coordinates(location: str) -> Tuple[bool, Any]:
    """
    Convert a city name into latitude/longitude coordinates.
    
    Args:
        location (str): City name like "London" or "New York,US"
        
    Returns:
        Tuple of (success: bool, location_data: dict or error_message: str)
    """
    # Build the geocoding API URL
    url = f"{GEO_URL}/direct?q={location}&limit=1&appid={API_KEY}"
    
    # Make the API request
    success, data = make_api_request(url)
    
    if not success:
        return False, data
        
    # Check if any locations were found
    if not data or len(data) == 0:
        return False, f"Location '{location}' not found"
        
    # Extract the coordinates and location info
    location_info = {
        "lat": data[0]["lat"],
        "lon": data[0]["lon"], 
        "name": data[0]["name"],
        "country": data[0].get("country", "")
    }
    
    return True, location_info


def get_current_weather_from_api(lat: float, lon: float) -> Tuple[bool, Any]:
    """
    Get current weather data for specific coordinates.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        Tuple of (success: bool, weather_data: dict or error_message: str)
    """
    # Build the current weather API URL
    url = f"{BASE_URL}/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    
    # Make the API request and return the result
    return make_api_request(url)


def get_forecast_from_api(lat: float, lon: float, days: int) -> Tuple[bool, Any]:
    """
    Get weather forecast data for specific coordinates.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude  
        days (int): Number of days to forecast (1-5)
        
    Returns:
        Tuple of (success: bool, forecast_data: dict or error_message: str)
    """
    # Each day has 8 forecast periods (every 3 hours), so multiply days by 8
    forecast_count = days * 8
    
    # Build the forecast API URL
    url = f"{BASE_URL}/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&cnt={forecast_count}"
    
    # Make the API request and return the result
    return make_api_request(url) 