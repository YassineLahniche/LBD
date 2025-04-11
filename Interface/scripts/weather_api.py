# Ajoutez ce code dans un nouveau fichier scripts/weather_api.py
import requests

# Constants
R = 287.05  # Specific gas constant for dry air in J/(kg·K)
API_URL = "https://api.open-meteo.com/v1/forecast"

# Wind turbine parameters (adjustable)
TURBINE_RADIUS = 50  # Radius of the wind turbine blades in meters
EFFICIENCY_WIND = 0.4  # Efficiency of the wind turbine (40%)

# Solar panel parameters (adjustable)
EFFICIENCY_SOLAR = 0.2  # Efficiency of the solar panels (20%)
SOLAR_CONSTANT = 1361  # Solar constant in W/m² (average solar radiation at the top of the atmosphere)

def fetch_weather_data(latitude, longitude):
    """
    Fetches hourly weather data from the Open-Meteo API, including solar radiation.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,pressure_msl,wind_speed_10m,is_day,shortwave_radiation",
        "timezone": "auto",
        "forecast_days": 7  # Get forecast for the next 7 days
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_wind_power(wind_speed, air_density=1.225):
    """
    Calculate potential wind power based on wind speed and turbine parameters
    """
    # P = 0.5 * ρ * A * v³ * Cp
    # where ρ is air density, A is swept area, v is wind speed, Cp is power coefficient
    area = 3.14159 * (TURBINE_RADIUS ** 2)
    power = 0.5 * air_density * area * (wind_speed ** 3) * EFFICIENCY_WIND
    return power

def calculate_solar_power(radiation):
    """
    Calculate potential solar power based on radiation data
    """
    # P = A * r * η
    # where A is area, r is radiation, η is efficiency
    # Assuming 1 m² of solar panel for simplicity
    area = 1.0  # m²
    power = area * radiation * EFFICIENCY_SOLAR
    return power

def get_forecast_data(latitude, longitude):
    """
    Returns processed forecast data for wind and solar power
    """
    weather_data = fetch_weather_data(latitude, longitude)
    
    if not weather_data:
        return None
    
    result = {
        "time": weather_data["hourly"]["time"],
        "temperature": weather_data["hourly"]["temperature_2m"],
        "wind_speed": weather_data["hourly"]["wind_speed_10m"],
        "radiation": weather_data["hourly"]["shortwave_radiation"],
        "wind_power": [],
        "solar_power": []
    }
    
    # Calculate potential power for each hour
    for i, wind_speed in enumerate(weather_data["hourly"]["wind_speed_10m"]):
        radiation = weather_data["hourly"]["shortwave_radiation"][i]
        
        wind_power = calculate_wind_power(wind_speed)
        solar_power = calculate_solar_power(radiation)
        
        result["wind_power"].append(wind_power)
        result["solar_power"].append(solar_power)
    
    return result