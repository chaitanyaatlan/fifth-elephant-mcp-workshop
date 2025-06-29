# Building a Weather MCP Server: Complete DIY Guide

A beginner-friendly tutorial for creating your first MCP server that provides weather data to Claude Desktop. This project demonstrates clean code organization, API integration, and MCP best practices.

## 🎯 What You'll Build

By the end of this guide, you'll have a fully functional MCP server that gives Claude Desktop two powerful weather tools:
- **Current Weather**: Get real-time weather conditions for any city
- **Weather Forecast**: Get 5-day weather predictions with detailed data

## 🏗️ Project Architecture

Our clean, modular architecture makes the code easy to understand and maintain:

```
fifth-elephant-mcp/
├── main.py           # MCP server and tool definitions
├── apis.py          # All API interactions with OpenWeather
├── utils.py         # Data formatting and validation utilities
├── pyproject.toml   # Project dependencies and configuration
├── .env            # Environment variables (API keys)
└── README.md       # This guide
```

**Why this structure?**
- **Separation of Concerns**: Each file has a specific purpose
- **Beginner-Friendly**: Easy to find and modify code
- **Maintainable**: Changes in one area don't affect others
- **Testable**: Functions can be tested independently

## 🚀 Step 1: Project Initialization

### 1.1 Create Project Directory
```bash
mkdir fifth-elephant-mcp
cd fifth-elephant-mcp
```

### 1.2 Initialize with UV
UV is a fast Python package manager that simplifies dependency management:

```bash
# Initialize a new Python project
uv init --quiet

# This creates:
# - pyproject.toml (project configuration)
# - .python-version (Python version specification)
# - A virtual environment
```

### 1.3 Add Dependencies
```bash
# Add MCP with CLI tools for development
uv add "mcp[cli]>=1.9.4"

# Add requests for HTTP API calls
uv add "requests>=2.32.4"

# Add python-dotenv for environment variable management
uv add python-dotenv
```

Your `pyproject.toml` should look like this:
```toml
[project]
name = "fifth-elephant-mcp"
version = "0.1.0"
description = "Weather MCP Server for Claude Desktop"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "mcp[cli]>=1.9.4",
    "requests>=2.32.4",
    "python-dotenv>=1.1.0",
]
```

## 🌤️ Step 2: Get Your Weather API Key

### 2.1 Sign up for OpenWeather API
1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Create a free account
3. Navigate to "API Keys" section
4. Copy your API key

### 2.2 Create Environment File
Create a `.env` file in your project root:
```bash
# .env
OPENWEATHER_API_KEY=your_api_key_here
```

**🔒 Security Note**: Never commit `.env` files to version control. Add `.env` to your `.gitignore`.

## 🏗️ Step 3: Building the API Layer

Create `apis.py` - our centralized API interaction module:

```python
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
    """Convert a city name into latitude/longitude coordinates."""
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
    """Get current weather data for specific coordinates."""
    # Build the current weather API URL
    url = f"{BASE_URL}/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    
    # Make the API request and return the result
    return make_api_request(url)


def get_forecast_from_api(lat: float, lon: float, days: int) -> Tuple[bool, Any]:
    """Get weather forecast data for specific coordinates."""
    # Each day has 8 forecast periods (every 3 hours), so multiply days by 8
    forecast_count = days * 8
    
    # Build the forecast API URL
    url = f"{BASE_URL}/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&cnt={forecast_count}"
    
    # Make the API request and return the result
    return make_api_request(url)
```

**🔑 Key Features of Our API Layer:**
- **Single Responsibility**: Each function has one job
- **Error Handling**: Consistent error handling across all API calls
- **Timeout Protection**: Prevents hanging requests
- **Type Hints**: Makes code self-documenting
- **Centralized Configuration**: All API settings in one place

## 🛠️ Step 4: Building the Utilities Layer

Create `utils.py` - our data processing and validation module:

```python
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
    """Check if the OpenWeather API key is configured."""
    if not API_KEY:
        return "OpenWeather API key not configured. Please set OPENWEATHER_API_KEY in your .env file."
    return None


def format_current_weather_response(weather_data: dict, location_data: dict) -> dict:
    """
    Format raw weather API data into a clean, organized structure.
    
    This function takes the messy API response and organizes it into
    easy-to-understand categories like temperature, weather condition, etc.
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
    """Format raw forecast API data into a clean, organized structure."""
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
    """
    # Make sure days is between 1 and 5
    return max(1, min(5, days))
```

**🎯 Why Separate Utilities:**
- **Reusability**: Functions can be used across different parts of the app
- **Testing**: Easy to test data formatting independently
- **Clarity**: Main server code focuses on MCP logic, not data processing

## 🖥️ Step 5: Building the MCP Server

Create `main.py` - the heart of our MCP server:

```python
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
```

**🔥 MCP Tool Best Practices Demonstrated:**
- **Rich Docstrings**: Help Claude understand what each tool does
- **Type Hints**: Make the code self-documenting
- **Error Handling**: Graceful failure with helpful error messages
- **Step-by-Step Logic**: Easy to follow and debug
- **Logging**: Helps with troubleshooting

## 🧪 Step 6: Local Testing

### 6.1 Test Your Server
```bash
# Run the server directly to check for errors
uv run python main.py

# You should see:
# 🚀 Weather MCP Server Starting...
# 📦 Modules loaded successfully
# INFO:__main__:🌤️  Weather MCP Server ready!
```

If you see any errors, check:
- ✅ Your `.env` file has the correct API key
- ✅ All dependencies are installed (`uv sync`)
- ✅ Python syntax is correct

### 6.2 Test with MCP Inspector (Optional)
The MCP Inspector is a development tool for testing your server:

```bash
# Install MCP development tools
npx @modelcontextprotocol/inspector uv run python main.py

# This opens a web interface where you can test your tools
```

## 🔗 Step 7: Claude Desktop Integration

### 7.1 Find Your Configuration File

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

### 7.2 Add Your Server Configuration

Edit the configuration file and add your weather server:

```json
{
  "mcpServers": {
    "weather-mcp": {
      "command": "/path/to/your/project/.venv/bin/python",
      "args": ["/path/to/your/project/main.py"]
    }
  }
}
```

**🎯 Pro Tips:**
- Use absolute paths for both `command` and `args`
- Find your Python path with: `uv run which python`
- Find your project path with: `pwd` (when inside project directory)

### 7.3 Alternative Configuration (Using UV)

If you prefer using UV directly:

```json
{
  "mcpServers": {
    "weather-mcp": {
      "command": "/Users/your-username/.local/bin/uv",
      "args": [
        "run", 
        "/path/to/your/project/main.py"
      ]
    }
  }
}
```

### 7.4 Restart Claude Desktop

**Important:** Always restart Claude Desktop completely after configuration changes:
1. Quit Claude Desktop (⌘+Q on Mac)
2. Reopen Claude Desktop
3. Look for your weather tools in Claude's interface

## 🎉 Step 8: Testing Your Weather Tools

### 8.1 Verify Tools Are Available
In Claude Desktop, you should see your weather tools are available. Claude might show a tools indicator or mention available weather capabilities.

### 8.2 Test Current Weather
Try these example queries:
- "What's the current weather in London?"
- "How warm is it in Tokyo right now?"
- "Is it raining in New York?"

### 8.3 Test Weather Forecast
Try these example queries:
- "What's the 5-day forecast for Paris?"
- "Will it rain in Seattle this week?"
- "What should I pack for Miami this weekend?"

### 8.4 Expected Response Format

**Current Weather Response:**
```json
{
  "location": {
    "name": "London",
    "country": "GB",
    "latitude": 51.5074,
    "longitude": -0.1278
  },
  "temperature": {
    "current": 15.5,
    "feels_like": 14.2,
    "minimum": 12.0,
    "maximum": 18.0
  },
  "weather_condition": {
    "main": "Clouds",
    "description": "overcast clouds",
    "icon": "04d"
  },
  "wind": {
    "speed": 3.5,
    "direction": 220
  },
  "atmosphere": {
    "humidity": 65,
    "pressure": 1013,
    "visibility": 10000,
    "cloudiness": 90
  },
  "sun": {
    "sunrise": "2025-01-29T07:45:00",
    "sunset": "2025-01-29T16:30:00"
  },
  "timestamp": "2025-01-29T14:00:00"
}
```

## 🐛 Common Issues & Solutions

### Issue 1: "Server disconnected" Error
**Symptoms:** Claude shows "Server disconnected" in logs

**Solutions:**
1. **Check paths in configuration:**
   ```bash
   # Verify Python path
   uv run which python
   
   # Verify project path
   pwd
   ```

2. **Test server manually:**
   ```bash
   uv run python main.py
   # Should show startup messages without errors
   ```

3. **Check configuration syntax:**
   ```bash
   # Validate JSON syntax
   python -m json.tool claude_desktop_config.json
   ```

### Issue 2: "API Key error"
**Symptoms:** Tools return "Invalid API key" errors

**Solutions:**
1. **Verify API key in .env file:**
   ```bash
   cat .env
   # Should show: OPENWEATHER_API_KEY=your_actual_key
   ```

2. **Test API key manually:**
   ```bash
   curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"
   ```

3. **Check API key is active:**
   - Log into OpenWeatherMap
   - Verify key is activated (can take a few hours)

### Issue 3: Tools Not Showing in Claude
**Symptoms:** Claude doesn't recognize weather tools

**Solutions:**
1. **Restart Claude Desktop completely**
2. **Check server is running:**
   - Look for your server in Claude's status/settings
3. **Verify configuration file location**
4. **Check file permissions:**
   ```bash
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

### Issue 4: "Module not found" Errors
**Symptoms:** ImportError for mcp, requests, etc.

**Solutions:**
1. **Reinstall dependencies:**
   ```bash
   uv sync
   ```

2. **Check virtual environment:**
   ```bash
   uv run pip list
   # Should show mcp, requests, python-dotenv
   ```

3. **Use full Python path in configuration**

## 🚀 Next Steps & Enhancements

### 🌟 Beginner Enhancements
1. **Add more locations:** Support for coordinates input
2. **Add weather alerts:** Integrate severe weather warnings
3. **Add air quality:** Include pollution data
4. **Add weather history:** Historical weather comparisons

### 🔥 Advanced Features
1. **Caching:** Store recent requests to improve performance
2. **Rate limiting:** Respect API limits
3. **Multiple APIs:** Fallback to other weather services
4. **Weather maps:** Generate visual weather representations

### 📊 Code Improvements
1. **Unit tests:** Add comprehensive test coverage
2. **Configuration management:** Support multiple API keys
3. **Logging enhancement:** Better error tracking
4. **Documentation:** Add inline code documentation

## 🎯 Key Takeaways

**✅ What You've Accomplished:**
- Built a production-ready MCP server with clean architecture
- Learned modular code organization (apis, utils, main)
- Implemented robust error handling and logging
- Created detailed documentation for AI understanding
- Successfully integrated with Claude Desktop

**🧠 Skills You've Developed:**
- MCP server development patterns
- API integration best practices
- Python project structure and organization
- Environment and dependency management
- Debugging and troubleshooting skills

**🔮 What's Next:**
- Explore other MCP servers and APIs
- Build more complex tools with multiple data sources
- Contribute to the MCP community
- Create your own custom AI assistants

---

## 📚 Resources & References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/modelcontextprotocol/python-sdk)
- [OpenWeather API Documentation](https://openweathermap.org/api)
- [UV Package Manager](https://github.com/astral-sh/uv)

## 🤝 Contributing

Found an issue or want to improve this guide? Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

---

**Happy coding! 🌤️** Your weather MCP server is now ready to provide Claude Desktop with powerful weather capabilities!
