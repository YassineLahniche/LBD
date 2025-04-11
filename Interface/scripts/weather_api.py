from flask import Flask, jsonify, request
from flask_cors import CORS  # Add this import
import requests
from datetime import datetime
import numpy as np
import math

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # Allow requests from your frontend

# Constants from your code
R = 287.05  # Specific gas constant for dry air in J/(kg·K)
TURBINE_RADIUS = 5  # Radius of the wind turbine blades in meters
EFFICIENCY_WIND = 0.4  # Efficiency of the wind turbine (40%)
EFFICIENCY_SOLAR = 0.2  # Efficiency of the solar panels (20%)

OPEN_METEO_API = "https://api.open-meteo.com/v1/forecast"

def calculate_wind_power(wind_speed_kmh, air_density=1.225, turbine_radius=TURBINE_RADIUS, efficiency=EFFICIENCY_WIND):
    """
    Calculates wind power generated using the wind power formula.

    Args:
        wind_speed_kmh (float): Wind speed in km/h.
        air_density (float): Air density in kg/m³.
        turbine_radius (float): Radius of the wind turbine blades in meters.
        efficiency (float): Efficiency of the wind turbine.

    Returns:
        float: Wind power generated in watts.
    """
    wind_speed_ms = wind_speed_kmh / 3.6  # Convert km/h to m/s
    swept_area = np.pi * turbine_radius**2  # A = πR²
    power = 0.5 * air_density * swept_area * wind_speed_ms**3 * efficiency
    return round(power, 2)

def calculate_solar_power(solar_radiation, efficiency=EFFICIENCY_SOLAR):
    """
    Calculates solar power generated based on solar radiation and daylight.

    Args:
        solar_radiation (float): Solar radiation in W/m².
        efficiency (float): Efficiency of the solar panels.

    Returns:
        float: Solar power generated in watts.
    """
    area = 1.0  # m²
    return round(solar_radiation * efficiency * area, 2)


def fetch_current_weather(latitude, longitude):
    """Fetch current weather data from Open-Meteo"""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m,shortwave_radiation",
        "timezone": "auto"
    }
    response = requests.get(OPEN_METEO_API, params=params)
    return response.json()

@app.route('/api/sensor/solar', methods=['GET'])
def get_solar_power():
    """Get current solar power generation"""
    lat = request.args.get('lat', 33.61)
    lon = request.args.get('lon', 7.65)
    
    weather_data = fetch_current_weather(lat, lon)
    radiation = weather_data['current']['shortwave_radiation']
    power = calculate_solar_power(radiation)
    
    return jsonify({
        "power": power,
        "radiation": radiation,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/sensor/wind', methods=['GET'])
def get_wind_power():
    """Get current wind power generation"""
    lat = request.args.get('lat', 33.61)
    lon = request.args.get('lon', 7.65)
    
    weather_data = fetch_current_weather(lat, lon)
    wind_speed = weather_data['current']['wind_speed_10m']
    power = calculate_wind_power(wind_speed)
    
    return jsonify({
        "power": power,
        "wind_speed": wind_speed,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/sensor/grid', methods=['GET'])
def get_grid_power():
    """Simulated grid consumption"""
    return jsonify({
        "power": 8500 + (500 * math.sin(datetime.now().minute)),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/forecast/<float:lat>/<float:lon>', methods=['GET'])
def get_forecast(lat, lon):
    """Get 7-day forecast with energy calculations"""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,wind_speed_10m,shortwave_radiation",
        "timezone": "auto",
        "forecast_days": 7
    }
    
    response = requests.get(OPEN_METEO_API, params=params)
    weather_data = response.json()
    
    result = {
        "time": weather_data["hourly"]["time"],
        "temperature": weather_data["hourly"]["temperature_2m"],
        "wind_speed": weather_data["hourly"]["wind_speed_10m"],
        "radiation": weather_data["hourly"]["shortwave_radiation"],
        "wind_power": [],
        "solar_power": []
    }
    
    for i in range(len(result["time"])):
        wind_power = calculate_wind_power(result["wind_speed"][i])
        solar_power = calculate_solar_power(result["radiation"][i])
        result["wind_power"].append(wind_power)
        result["solar_power"].append(solar_power)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)