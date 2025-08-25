import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_external_dependencies_availability_handling():
    # Endpoints to test
    forecast_endpoint = f"{BASE_URL}/get_forecast"
    alerts_endpoint = f"{BASE_URL}/get_alerts"
    healthcheck_endpoint = f"{BASE_URL}/healthcheck"  # assuming health check endpoint exists as per instructions

    # Valid parameters
    valid_forecast_params = {"latitude": 40.7128, "longitude": -74.0060}  # New York City coordinates
    valid_alerts_params = {"state": "NY"}

    # Invalid parameters
    invalid_forecast_params = {"latitude": "invalid", "longitude": "invalid"}
    invalid_alerts_params = {"state": "XX"}  # non-existing US state code

    headers = {
        "Accept": "application/json"
    }

    # 1. Test Weather Forecast endpoint with valid parameters
    try:
        resp = requests.get(forecast_endpoint, params=valid_forecast_params, headers=headers, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Expected 200 OK for valid forecast request, got {resp.status_code}"
        data = resp.json()
        assert "forecast" in data or "properties" in data, "Response missing expected forecast data"
    except (Timeout, ConnectionError):
        # External dependency (NWS API or internet) may be down - assert appropriate error handling
        # Assuming server returns 503 Service Unavailable or similar
        resp = requests.get(forecast_endpoint, params=valid_forecast_params, headers=headers, timeout=TIMEOUT)
        assert resp.status_code in [503, 504], f"Expected 503/504 on external dependency failure, got {resp.status_code}"
    except RequestException as e:
        assert False, f"Request failed unexpectedly: {e}"

    # 2. Test Weather Forecast endpoint with invalid parameters
    try:
        resp = requests.get(forecast_endpoint, params=invalid_forecast_params, headers=headers, timeout=TIMEOUT)
        assert resp.status_code in [400, 422], f"Expected 400 or 422 for invalid forecast params, got {resp.status_code}"
        error_data = resp.json()
        assert "error" in error_data or "message" in error_data, "Expected error message in response for invalid params"
    except RequestException as e:
        assert False, f"Request with invalid params failed unexpectedly: {e}"

    # 3. Test Weather Alerts endpoint with valid parameters
    try:
        resp = requests.get(alerts_endpoint, params=valid_alerts_params, headers=headers, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Expected 200 OK for valid alerts request, got {resp.status_code}"
        data = resp.json()
        assert "alerts" in data or "features" in data, "Response missing expected alerts data"
    except (Timeout, ConnectionError):
        # External dependency may be down - expect proper error handling
        resp = requests.get(alerts_endpoint, params=valid_alerts_params, headers=headers, timeout=TIMEOUT)
        assert resp.status_code in [503, 504], f"Expected 503/504 on external dependency failure, got {resp.status_code}"
    except RequestException as e:
        assert False, f"Request to alerts endpoint failed unexpectedly: {e}"

    # 4. Test Weather Alerts endpoint with invalid parameters
    try:
        resp = requests.get(alerts_endpoint, params=invalid_alerts_params, headers=headers, timeout=TIMEOUT)
        assert resp.status_code in [400, 422], f"Expected 400 or 422 for invalid alerts params, got {resp.status_code}"
        error_data = resp.json()
        assert "error" in error_data or "message" in error_data, "Expected error message in response for invalid alerts params"
    except RequestException as e:
        assert False, f"Request with invalid alert params failed unexpectedly: {e}"

    # 5. Test Health Check endpoint for overall server health and handling of external dependencies
    # Assumes a healthcheck endpoint "/healthcheck" exists to check server status and external dependencies
    try:
        resp = requests.get(healthcheck_endpoint, headers=headers, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Expected 200 OK from health check, got {resp.status_code}"
        health_data = resp.json()
        # Assuming health endpoint returns at least 'external_dependencies' key with statuses
        assert "external_dependencies" in health_data, "Health check missing external_dependencies info"
        ext_deps = health_data["external_dependencies"]
        # external_dependencies should be a dict with keys like "NWS_API" and "internet"
        assert isinstance(ext_deps, dict), "external_dependencies should be a dictionary"
        # Validate presence of keys and their boolean status or status string
        assert any(k.lower() in ["nws_api", "internet", "connectivity"] for k in ext_deps.keys()), "Expected keys about NWS API or internet connectivity"
    except (Timeout, ConnectionError):
        # If health endpoint itself is unreachable, it may indicate server or dependencies down
        assert False, "Health check endpoint unreachable, possible server or external dependency failure."
    except RequestException as e:
        assert False, f"Health check request failed unexpectedly: {e}"

test_external_dependencies_availability_handling()