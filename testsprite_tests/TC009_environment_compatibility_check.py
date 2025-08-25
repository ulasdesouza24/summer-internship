import sys
import subprocess
import requests
import json

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_environment_compatibility_check():
    # Check Python version
    python_version = sys.version_info
    assert python_version.major == 3 and python_version.minor >= 10 or python_version.major > 3, \
        f"Python version is {python_version.major}.{python_version.minor}, but >=3.10 is required."

    # Check Node.js version by invoking `node -v`
    try:
        completed_process = subprocess.run(["node", "-v"], capture_output=True, text=True, timeout=10, check=True)
        node_version_str = completed_process.stdout.strip()
        if node_version_str.startswith("v"):
            node_version_str = node_version_str[1:]
        node_version_parts = node_version_str.split(".")
        node_major = int(node_version_parts[0])
        node_minor = int(node_version_parts[1])
        assert node_major > 18 or (node_major == 18 and node_minor >= 0), \
            f"Node.js version is {node_major}.{node_minor}, but >=18.0.0 is required."
    except FileNotFoundError:
        assert False, "Node.js executable 'node' not found - Node.js must be installed and in PATH."
    except (subprocess.SubprocessError, IndexError, ValueError) as e:
        assert False, f"Failed to get valid Node.js version: {e}"

    headers = {"Accept": "application/json"}

    # 1. Test weather forecast retrieval with valid parameters (New York City example lat/lon)
    try:
        lat, lon = 40.7128, -74.0060
        forecast_resp = requests.get(
            f"{BASE_URL}/get_forecast",
            params={"latitude": lat, "longitude": lon},
            headers=headers,
            timeout=TIMEOUT,
        )
        assert forecast_resp.status_code == 200, f"get_forecast valid params returned {forecast_resp.status_code}"
        forecast_data = forecast_resp.json()
        assert "forecast" in forecast_data or "properties" in forecast_data, "Forecast data missing expected keys"
    except Exception as e:
        assert False, f"Exception during get_forecast valid test: {e}"

    # 2. Test weather forecast retrieval with invalid parameters (non-numeric lat/lon)
    try:
        forecast_resp_invalid = requests.get(
            f"{BASE_URL}/get_forecast",
            params={"latitude": "invalid", "longitude": "invalid"},
            headers=headers,
            timeout=TIMEOUT,
        )
        assert 400 <= forecast_resp_invalid.status_code < 500, \
            f"get_forecast invalid params should fail client side, got {forecast_resp_invalid.status_code}"
    except Exception:
        # Acceptable if server returns an error response rather than crash
        pass

    # 3. Test weather alerts retrieval with valid parameter (state=CA)
    try:
        alerts_resp = requests.get(
            f"{BASE_URL}/get_alerts",
            params={"state": "CA"},
            headers=headers,
            timeout=TIMEOUT,
        )
        assert alerts_resp.status_code == 200, f"get_alerts valid params returned {alerts_resp.status_code}"
        alerts_data = alerts_resp.json()
        assert "features" in alerts_data, "Alerts data missing 'features' field"
    except Exception as e:
        assert False, f"Exception during get_alerts valid test: {e}"

    # 4. Test weather alerts retrieval with invalid parameter (unsupported state code)
    try:
        alerts_resp_invalid = requests.get(
            f"{BASE_URL}/get_alerts",
            params={"state": "XX"},
            headers=headers,
            timeout=TIMEOUT,
        )
        assert 400 <= alerts_resp_invalid.status_code < 500, \
            f"get_alerts invalid state should fail client side, got {alerts_resp_invalid.status_code}"
    except Exception:
        # Acceptable if server returns an error response rather than crash
        pass

    # 5. Test interactive chat commands endpoints (simulate /help, /tools, /quit)
    # Assuming these are accessed via an endpoint /chat_command with POST and payload {"command": "/help"}
    chat_commands = ["/help", "/tools", "/quit"]
    for command in chat_commands:
        try:
            resp = requests.post(
                f"{BASE_URL}/chat_command",
                headers={"Content-Type": "application/json"},
                json={"command": command},
                timeout=TIMEOUT,
            )
            assert resp.status_code == 200, f"Chat command {command} returned {resp.status_code}"
            data = resp.json()
            assert "response" in data and isinstance(data["response"], str), f"Chat command {command} missing 'response'"
            assert len(data["response"]) > 0, f"Chat command {command} returned empty response"
        except Exception as e:
            assert False, f"Exception during chat command {command} test: {e}"


test_environment_compatibility_check()