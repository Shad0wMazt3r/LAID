class WeatherService:
    @staticmethod
    def get_weather(location):
        weather_data = {
            "paris": {"temperature": "22°C", "condition": "Sunny", "humidity": "65%"},
            "london": {"temperature": "18°C", "condition": "Cloudy", "humidity": "80%"},
            "tokyo": {"temperature": "25°C", "condition": "Rainy", "humidity": "90%"}
        }
        
        location_key = location.lower()
        if location_key in weather_data:
            return weather_data[location_key]
        else:
            return {"error": f"Weather data not available for {location}"}