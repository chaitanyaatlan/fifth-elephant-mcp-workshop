"""
Utility Functions

This file contains helper functions for validation, formatting, and other utilities.
These functions process data and make it easier to work with.
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("OPENWEATHER_API_KEY")


def validate_api_key() -> Optional[str]:
    """
    Check if the OpenWeather API key is configured.
    
    Returns:
        None if API key exists, or error message string if missing
    """
    if not API_KEY:
        return "OpenWeather API key not configured. Please set OPENWEATHER_API_KEY in your .env file."
    return None


def format_current_weather_response(weather_data: dict, location_data: dict) -> dict:
    """
    Format raw weather API data into a clean, organized structure.
    
    This function takes the messy API response and organizes it into
    easy-to-understand categories like temperature, weather condition, etc.
    
    Args:
        weather_data (dict): Raw weather data from API
        location_data (dict): Location information (name, country, coordinates)
        
    Returns:
        dict: Nicely formatted weather data
    """
    return {
        # Location information
        "location": {
            "name": location_data["name"],
            "country": location_data["country"],
            "latitude": location_data["lat"],
            "longitude": location_data["lon"]
        },
        
        # Temperature information (all in Celsius)
        "temperature": {
            "current": weather_data["main"]["temp"],
            "feels_like": weather_data["main"]["feels_like"],
            "minimum": weather_data["main"]["temp_min"],
            "maximum": weather_data["main"]["temp_max"]
        },
        
        # Weather condition (sunny, cloudy, rainy, etc.)
        "weather_condition": {
            "main": weather_data["weather"][0]["main"],
            "description": weather_data["weather"][0]["description"],
            "icon": weather_data["weather"][0]["icon"]
        },
        
        # Wind information
        "wind": {
            "speed": weather_data["wind"]["speed"],  # meters per second
            "direction": weather_data["wind"]["deg"]  # degrees
        },
        
        # Other atmospheric data
        "atmosphere": {
            "humidity": weather_data["main"]["humidity"],      # percentage
            "pressure": weather_data["main"]["pressure"],     # hPa
            "visibility": weather_data.get("visibility", 0),  # meters
            "cloudiness": weather_data["clouds"]["all"]       # percentage
        },
        
        # Sun times
        "sun": {
            "sunrise": datetime.fromtimestamp(weather_data["sys"]["sunrise"]).isoformat(),
            "sunset": datetime.fromtimestamp(weather_data["sys"]["sunset"]).isoformat()
        },
        
        # When this data was recorded
        "timestamp": datetime.fromtimestamp(weather_data["dt"]).isoformat()
    }


def format_forecast_response(forecast_data: dict, location_data: dict, days: int) -> dict:
    """
    Format raw forecast API data into a clean, organized structure.
    
    Args:
        forecast_data (dict): Raw forecast data from API
        location_data (dict): Location information
        days (int): Number of days requested
        
    Returns:
        dict: Nicely formatted forecast data
    """
    # Process each forecast item (every 3 hours)
    forecast_items = []
    for item in forecast_data["list"]:
        forecast_items.append({
            # When this forecast is for
            "datetime": datetime.fromtimestamp(item["dt"]).isoformat(),
            
            # Temperature data
            "temperature": {
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "min": item["main"]["temp_min"],
                "max": item["main"]["temp_max"]
            },
            
            # Weather condition
            "weather_condition": {
                "main": item["weather"][0]["main"],
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"]
            },
            
            # Wind data
            "wind": {
                "speed": item["wind"]["speed"],
                "direction": item["wind"]["deg"]
            },
            
            # Atmospheric conditions
            "atmosphere": {
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "cloudiness": item["clouds"]["all"],
                "visibility": item.get("visibility", 0)
            },
            
            # Chance of precipitation (rain/snow)
            "precipitation_probability": item.get("pop", 0)  # 0-1 (0% to 100%)
        })
    
    return {
        # Location information
        "location": {
            "name": location_data["name"],
            "country": location_data["country"],
            "latitude": location_data["lat"],
            "longitude": location_data["lon"]
        },
        
        # All forecast items (every 3 hours)
        "forecast": forecast_items,
        
        # How many days were requested
        "days_requested": days,
        
        # Total number of forecast periods
        "total_forecasts": len(forecast_items)
    }


def validate_forecast_days(days: int) -> int:
    """
    Validate and limit the number of forecast days.
    
    OpenWeather API only allows 1-5 days of forecast data.
    
    Args:
        days (int): Requested number of days
        
    Returns:
        int: Valid number of days (between 1 and 5)
    """
    # Make sure days is between 1 and 5
    return max(1, min(5, days)) 