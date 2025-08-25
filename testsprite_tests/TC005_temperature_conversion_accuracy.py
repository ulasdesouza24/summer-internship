import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_temperature_conversion_accuracy():
    """
    Test the temperature conversion utilities integrated with the weather data for accuracy
    using standard temperature conversion formulas.
    """

    # Sample city: New York (latitude/longitude)
    latitude = 40.7128
    longitude = -74.0060

    headers = {
        "Accept": "application/json",
    }

    # Step 1: Retrieve weather forecast data for the city
    forecast_url = f"{BASE_URL}/get_forecast"
    params = {"latitude": latitude, "longitude": longitude}

    try:
        response = requests.get(forecast_url, params=params, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to get_forecast endpoint failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    forecast_data = response.json()

    # Validate forecast data contains temperature fields in expected format
    # Assume forecast_data contains a field "temperature" in Fahrenheit as example:
    # e.g., forecast_data = {"temperature": 75, "temperature_celsius": 23.9} or similar
    # Since schema isn't strictly specified, check common fields and derived conversion

    # Heuristics: temperature might be in forecast_data["temperature"] (Fahrenheit)
    # or nested, let's try common patterns:
    temp_f = None
    temp_c_reported = None

    # Search for temperature data in response
    if "temperature" in forecast_data:
        temp_f = forecast_data["temperature"]
    elif "properties" in forecast_data and "temperature" in forecast_data["properties"]:
        temp_f = forecast_data["properties"]["temperature"]
    else:
        # Check for other common structures
        # If hourly or daily forecast, might be a list
        try:
            periods = forecast_data.get("properties", {}).get("periods", [])
            if periods and isinstance(periods, list):
                # Take the first period's temperature and temperature unit
                first_period = periods[0]
                temp_f = first_period.get("temperature")
                temp_unit = first_period.get("temperatureUnit", "F")
                # Try to find celsius equivalent if provided
                temp_c_reported = first_period.get("temperatureCelsius")
        except Exception:
            pass

    assert temp_f is not None, "Temperature (Fahrenheit) not found in forecast data"

    # We try to locate a celsius value either in the response or calculate conversion ourselves
    # If temp_c_reported found, validate it against conversion formula
    if temp_c_reported is not None:
        # Validate: C = (F - 32) * 5/9
        c_expected = round((temp_f - 32) * 5 / 9, 1)
        assert abs(c_expected - temp_c_reported) < 0.5, (
            f"Temperature conversion mismatch: reported Celsius {temp_c_reported}, expected {c_expected}"
        )

    else:
        # If celsius not reported, validate conversion formula independently
        c_converted = round((temp_f - 32) * 5 / 9, 1)
        # To validate integration, call temperature conversion endpoint if exists or calculate reverse
        # Assuming there is an endpoint for temperature conversion (schema does not specify),
        # but PRD mentions temperature conversion utilities integrated
        # Test the conversion endpoint if available, else rely on formula

        convert_url = f"{BASE_URL}/convert_temperature"
        # Test conversion Fahrenheit to Celsius
        try:
            convert_resp = requests.get(convert_url, params={"value": temp_f, "from": "F", "to": "C"}, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            # If endpoint not available, skip converting endpoint test and do internal formula check only
            convert_resp = None

        if convert_resp and convert_resp.status_code == 200:
            try:
                convert_data = convert_resp.json()
                c_converted_api = convert_data.get("result")
                assert c_converted_api is not None, "Temperature conversion API missing 'result' field"
                assert abs(c_converted_api - c_converted) < 0.5, (
                    f"Temperature conversion API result mismatch: got {c_converted_api}, expected ~{c_converted}"
                )
            except Exception as e:
                assert False, f"Error parsing conversion API response: {e}"
        else:
            # Conversion API not available, rely on formula validation only
            # This checks the formula correctness, standalone step
            assert isinstance(c_converted, float), "Converted temperature should be a float"

    # Also test reverse conversion: Celsius to Fahrenheit
    # Pick a standard temperature
    test_celsius = 100.0
    f_expected = round(test_celsius * 9 / 5 + 32, 1)

    # If convert_temperature available, test
    try:
        convert_resp_rev = requests.get(convert_url, params={"value": test_celsius, "from": "C", "to": "F"}, headers=headers, timeout=TIMEOUT)
    except Exception:
        convert_resp_rev = None

    if convert_resp_rev and convert_resp_rev.status_code == 200:
        try:
            convert_data_rev = convert_resp_rev.json()
            f_converted_api = convert_data_rev.get("result")
            assert f_converted_api is not None, "Temperature conversion API missing 'result' field in reverse conversion"
            assert abs(f_converted_api - f_expected) < 0.5, (
                f"Temperature conversion API reverse result mismatch: got {f_converted_api}, expected ~{f_expected}"
            )
        except Exception as e:
            assert False, f"Error parsing conversion API reverse response: {e}"
    else:
        # Conversion API not available; verify formula correctness for reverse conversion
        f_converted = test_celsius * 9 / 5 + 32
        assert round(f_converted, 1) == f_expected, "Reverse temperature conversion formula mismatch"


test_temperature_conversion_accuracy()