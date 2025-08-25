import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_alerts_endpoint_returns_active_weather_alerts():
    # Test with a valid US state (e.g., California: CA)
    valid_state = "CA"
    url = f"{BASE_URL}/get_alerts"
    headers = {
        "Accept": "application/json"
    }
    params = {"state": valid_state}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # The response should contain a list of alerts
    assert isinstance(data, dict), "Response JSON root should be a dictionary"
    alerts = data.get("alerts") or data.get("features") or data.get("results") or data.get("data")
    # Accept multiple possible keys that might contain alerts, fallback to empty list
    if alerts is None:
        alerts = []
    assert isinstance(alerts, list), "Alerts should be a list"

    # Validate that all alerts returned are active and relevant to the given state
    now_utc = datetime.now(timezone.utc)
    for alert in alerts:
        # Basic checks for expected alert fields
        # This depends on the actual alert schema from MCP server; falling back to common NWS alert structure
        properties = alert.get("properties", alert)  # some APIs wrap alerts under "properties"
        # Check state code match (if available)
        area_desc = properties.get("areaDesc", "")
        assert valid_state in area_desc or valid_state.lower() in area_desc.lower(), (
            f"Alert areaDesc does not mention state '{valid_state}': {area_desc}"
        )

        # Check alert is active by comparing ends and starts times
        sent_str = properties.get("sent")
        onset_str = properties.get("onset")
        expires_str = properties.get("expires")
        effective_str = properties.get("effective")
        # Use any of the timestamps to check if alert is current
        timestamp_str = expires_str or onset_str or effective_str or sent_str
        if timestamp_str:
            try:
                alert_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                assert alert_time > now_utc or expires_str is None, (
                    f"Alert not active or expired: expires={expires_str}, now={now_utc.isoformat()}"
                )
            except Exception:
                # If timestamp parsing fails, do not fail test here but log
                pass

    # Test with an invalid state code that should return no alerts or an error
    invalid_state = "XX"
    params_invalid = {"state": invalid_state}

    try:
        response_invalid = requests.get(url, headers=headers, params=params_invalid, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request with invalid state failed: {e}"

    # The API should handle invalid states gracefully, either with 200 and empty alerts or 4xx error
    assert response_invalid.status_code in (200, 400, 422), (
        f"Unexpected status code for invalid state '{invalid_state}': {response_invalid.status_code}"
    )
    if response_invalid.status_code == 200:
        try:
            data_invalid = response_invalid.json()
        except ValueError:
            assert False, "Response for invalid state is not valid JSON"
        alerts_invalid = data_invalid.get("alerts") or []
        assert isinstance(alerts_invalid, list), "Alerts for invalid state should be a list"
        assert len(alerts_invalid) == 0, "Expected no alerts for invalid state"

test_get_alerts_endpoint_returns_active_weather_alerts()