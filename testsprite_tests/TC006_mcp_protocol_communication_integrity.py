import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}

def test_mcp_protocol_communication_integrity():
    # Test weather forecast retrieval with valid parameters
    valid_forecast_payload = {"latitude": 40.7128, "longitude": -74.0060}  # New York coordinates
    try:
        resp = requests.post(f"{BASE_URL}/get_forecast", json=valid_forecast_payload, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # Assert presence of 'periods' in nested properties
        assert "properties" in data and "periods" in data["properties"], "Expected 'periods' in forecast response properties"
    except Exception as e:
        assert False, f"Valid forecast request failed: {e}"

    # Test weather forecast retrieval with invalid parameters
    invalid_forecast_payload = {"latitude": "invalid", "longitude": "invalid"}
    resp = requests.post(f"{BASE_URL}/get_forecast", json=invalid_forecast_payload, headers=HEADERS, timeout=TIMEOUT)
    assert resp.status_code >= 400, "Invalid forecast parameters should return error status code"

    # Test weather alerts retrieval with valid state parameter
    valid_alerts_payload = {"state": "NY"}
    try:
        resp = requests.post(f"{BASE_URL}/get_alerts", json=valid_alerts_payload, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # Assert alerts present as 'features' list
        assert "features" in data and isinstance(data["features"], list), "Expected 'features' list in alerts response"
    except Exception as e:
        assert False, f"Valid alerts request failed: {e}"

    # Test weather alerts retrieval with invalid state parameter
    invalid_alerts_payload = {"state": "XX"}
    resp = requests.post(f"{BASE_URL}/get_alerts", json=invalid_alerts_payload, headers=HEADERS, timeout=TIMEOUT)
    assert resp.status_code >= 400, "Invalid alerts parameters should return error status code"

    # Test interactive chat commands functionality (/help, /tools, /quit)
    chat_commands = ["/help", "/tools", "/quit"]
    for cmd in chat_commands:
        resp = requests.post(f"{BASE_URL}/chat", json={"command": cmd}, headers=HEADERS, timeout=TIMEOUT)
        try:
            resp.raise_for_status()
            data = resp.json()
            assert "response" in data, f"Chat command {cmd} should return a response"
            assert len(data["response"]) > 0, f"Chat command {cmd} response should not be empty"
        except Exception as e:
            assert False, f"Chat command {cmd} failed: {e}"

test_mcp_protocol_communication_integrity()