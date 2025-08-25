import requests

def test_get_forecast_endpoint_returns_correct_weather_data():
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/get_forecast"
    timeout = 30
    # Example valid coordinates for New York City (one of supported US cities)
    params = {
        "latitude": 40.7128,
        "longitude": -74.0060,
    }
    headers = {
        "Accept": "application/json",
    }

    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to get_forecast endpoint failed: {e}"

    # Assert response content type is JSON
    content_type = response.headers.get('Content-Type', '')
    assert 'application/json' in content_type, f"Expected JSON response content type but got {content_type}"

    data = response.json()

    # Validate response structure and content based on typical weather forecast data
    # Expecting keys like 'forecast', 'location', 'temperature', 'conditions', etc.
    assert isinstance(data, dict), "Response JSON root should be an object"

    # Basic keys checks (not exhaustive, but essential)
    assert "forecast" in data, "Response missing 'forecast' key"
    assert isinstance(data["forecast"], dict), "'forecast' should be an object"

    # Forecast should have periods, temperature, wind, and conditions maybe
    forecast = data["forecast"]
    assert "periods" in forecast, "'forecast' missing 'periods' key"
    periods = forecast["periods"]
    assert isinstance(periods, list), "'periods' should be a list"
    assert len(periods) > 0, "'periods' list should not be empty"

    # Validate each period item for expected keys
    period_keys = {"name", "startTime", "temperature", "temperatureUnit", "windSpeed", "windDirection", "shortForecast"}
    for period in periods:
        assert isinstance(period, dict), "Each period should be a dictionary"
        missing_keys = period_keys - period.keys()
        assert not missing_keys, f"Period missing keys: {missing_keys}"

    # Validate location in response matches roughly the requested coords if present
    if "location" in data and isinstance(data["location"], dict):
        location = data["location"]
        assert "latitude" in location and "longitude" in location, "Location info should include latitude and longitude"
        # Allow small delta for matching since forecast might be for broader area
        lat_diff = abs(location["latitude"] - params["latitude"])
        lon_diff = abs(location["longitude"] - params["longitude"])
        assert lat_diff < 1.0, f"Latitude in response ({location['latitude']}) differs too much from requested ({params['latitude']})"
        assert lon_diff < 1.0, f"Longitude in response ({location['longitude']}) differs too much from requested ({params['longitude']})"

    # Timestamp validation - forecast should be up to date (optional if timestamp provided)
    # For brevity, not implemented as it depends on API spec.

test_get_forecast_endpoint_returns_correct_weather_data()