from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

IPINFO_TOKEN = os.getenv('IPINFO_TOKEN')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

@app.route("/api/hello")
def greeting():
    try:
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        print(f"Client IP: {client_ip}")
        
        visitor_name = request.args.get("visitor_name", default='Guest', type=str)
        print(f"Visitor Name: {visitor_name}")
        
        client_info = get_client_city(client_ip)
        print(f"Client Info: {client_info}")
        
        city = client_info.get("city", "New York")
        lat = client_info.get("lat", 40.7128)
        lon = client_info.get('lon', -74.0060)
        print(f"City: {city}, Latitude: {lat}, Longitude: {lon}")
        
        if lat and lon:
            weather_info = get_weather_info(lat, lon)
            print(f"Weather Info: {weather_info}")
            if weather_info:
                temp = weather_info.get('main', {}).get('temp')
                if temp is not None:
                    response = {
                        "client_ip": client_ip,
                        "location": city,
                        "greeting": f"Hello, {visitor_name}! The temperature is {int(temp)} degrees Celsius in {city}."
                    }
                    return jsonify(response), 200
        return jsonify({"error": "Failed to retrieve weather information."}), 500
    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return jsonify({
        "Message": "Welcome to Home Page"
    })

def get_client_city(ip_address):
    try:
        url = f"https://ipinfo.io/{ip_address}/json"
        headers = {
            "Authorization": f"Bearer {IPINFO_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        print(f"IPInfo Response: {response.json()}")
        if response.status_code == 200:
            data = response.json()
            city = data.get("city", "New York")
            loc = data.get("loc", "").split(',')
            if len(loc) == 2:
                lat = loc[0]
                lon = loc[1]
                return {"city": city, "lat": lat, "lon": lon}
        return {"city": "New York", "lat": 40.7128, "lon": -74.0060}
    except Exception as e:
        print(f"Error getting city information: {str(e)}")
        return {"city": "New York", "lat": 40.7128, "lon": -74.0060}

def get_weather_info(latitude, longitude):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": OPENWEATHERMAP_API_KEY,
            "units": "metric"
        }
        response = requests.get(url, params=params)
        print(f"Weather API Response: {response.json()}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting weather information: {str(e)}")
        return None

if __name__ == "__main__":
    app.run(debug=True)
