class WeatherService:
    WEATHER_DATA = {
        "paris": {"temperature": "22°C", "condition": "Sunny", "humidity": "65%"},
        "london": {"temperature": "18°C", "condition": "Cloudy", "humidity": "80%"},
        "tokyo": {"temperature": "25°C", "condition": "Rainy", "humidity": "90%"},
    }

    @classmethod
    def get_weather(cls, location):
        return cls.WEATHER_DATA.get(
            location.lower(), {"error": f"Weather data not available for {location}"}
        )
