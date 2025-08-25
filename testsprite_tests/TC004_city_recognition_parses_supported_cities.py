import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Supported cities and their known coordinates (latitude, longitude)
SUPPORTED_CITIES_COORDS = {
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "Houston": (29.7604, -95.3698),
    "Phoenix": (33.4484, -112.0740),
    "Philadelphia": (39.9526, -75.1652),
    "San Antonio": (29.4241, -98.4936),
    "San Diego": (32.7157, -117.1611),
    "Dallas": (32.7767, -96.7970),
    "San Jose": (37.3382, -121.8863),
    "Austin": (30.2672, -97.7431),
    "Jacksonville": (30.3322, -81.6557),
    "San Francisco": (37.7749, -122.4194),
    "Columbus": (39.9612, -82.9988),
    "Charlotte": (35.2271, -80.8431),
    "Fort Worth": (32.7555, -97.3308),
    "Detroit": (42.3314, -83.0458),
    "El Paso": (31.7619, -106.4850),
    "Memphis": (35.1495, -90.0490),
    "Seattle": (47.6062, -122.3321),
    "Denver": (39.7392, -104.9903),
    "Washington": (38.9072, -77.0369),
    "Boston": (42.3601, -71.0589),
    "Nashville": (36.1627, -86.7816),
    "Baltimore": (39.2904, -76.6122),
    "Oklahoma City": (35.4676, -97.5164),
    "Portland": (45.5051, -122.6750),
    "Las Vegas": (36.1699, -115.1398),
    "Milwaukee": (43.0389, -87.9065),
    "Albuquerque": (35.0844, -106.6504),
    "Tucson": (32.2226, -110.9747),
    "Fresno": (36.7378, -119.7871),
    "Sacramento": (38.5816, -121.4944),
    "Miami": (25.7617, -80.1918),
    "Kansas City": (39.0997, -94.5786),
    "Mesa": (33.4152, -111.8315),
    "Atlanta": (33.749, -84.388),
    "Omaha": (41.2565, -95.9345),
    "Raleigh": (35.7796, -78.6382),
    "Colorado Springs": (38.8339, -104.8214),
    "Virginia Beach": (36.8529, -75.978)
}

def city_recognition_parses_supported_cities():
    session = requests.Session()
    headers = {
        "Accept": "application/json"
    }
    for city, (lat, lon) in SUPPORTED_CITIES_COORDS.items():
        try:
            response = session.get(
                f"{BASE_URL}/get_forecast",
                params={"latitude": lat, "longitude": lon},
                headers=headers,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            # Validate response contains expected keys relevant to a forecast response
            assert "properties" in data, f"Missing 'properties' in forecast response for city {city}"
            properties = data["properties"]
            assert "periods" in properties, f"Missing 'periods' in 'properties' for city {city}"
            forecast_periods = properties["periods"]
            assert isinstance(forecast_periods, list) and len(forecast_periods) > 0, f"No forecast periods returned for city {city}"

        except requests.exceptions.RequestException as e:
            assert False, f"Request failed for city {city} with error: {e}"
        except (ValueError, AssertionError) as e:
            assert False, f"Validation failed for city {city}: {e}"

    session.close()


city_recognition_parses_supported_cities()
