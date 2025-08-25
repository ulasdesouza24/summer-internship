import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def test_handle_invalid_location_inputs_gracefully():
    """
    Test the system's robustness in handling unsupported or invalid location inputs
    by providing user guidance and error messages for weather forecast, weather alerts,
    and interactive chat endpoints.
    """
    # Invalid coordinates (latitude and longitude out of range)
    invalid_coords = [
        {"latitude": 1000, "longitude": 2000},  # clearly invalid
        {"latitude": -999, "longitude": 50},
        {"latitude": 40, "longitude": -999},
        {"latitude": "abc", "longitude": "def"},  # invalid type
        {"latitude": None, "longitude": None},
    ]

    # Test get_forecast endpoint with invalid location inputs
    forecast_url = f"{BASE_URL}/get_forecast"
    for coords in invalid_coords:
        try:
            response = requests.get(
                forecast_url,
                params={"latitude": coords["latitude"], "longitude": coords["longitude"]},
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            assert response.status_code in (400, 422, 404), (
                f"Expected 400, 422 or 404 status for invalid coords {coords}, got {response.status_code}"
            )
            try:
                json_resp = response.json()
            except Exception:
                assert False, f"No JSON response for invalid coords {coords} with status {response.status_code}"
            assert (
                "error" in json_resp or "message" in json_resp
            ), f"Expected error message in response for coords {coords}"
            # Optional: check for guidance message/key phrases
            guidance = json_resp.get("error") or json_resp.get("message")
            assert (
                "invalid" in guidance.lower() or "unsupported" in guidance.lower()
            ), f"Expected user guidance in error message for coords {coords}"
        except requests.RequestException as e:
            assert False, f"RequestException raised for forecast invalid coords {coords}: {e}"

    # Invalid states for get_alerts endpoint
    invalid_states = ["XX", "InvalidState", "123", "", None, "NewYrok"]
    alerts_url = f"{BASE_URL}/get_alerts"
    for state in invalid_states:
        try:
            response = requests.get(
                alerts_url,
                params={"state": state},
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            # System can return 400, 422 or 404 depending on implementation
            assert response.status_code in (400, 422, 404), (
                f"Expected 400, 422 or 404 for invalid state '{state}', got {response.status_code}"
            )
            try:
                json_resp = response.json()
            except Exception:
                assert False, f"No JSON response for invalid state '{state}' with status {response.status_code}"
            assert (
                "error" in json_resp or "message" in json_resp
            ), f"Expected error message in response for invalid state '{state}'"
            guidance = json_resp.get("error") or json_resp.get("message")
            assert (
                "invalid" in guidance.lower()
                or "unsupported" in guidance.lower()
                or "not found" in guidance.lower()
            ), f"Expected user guidance in error message for invalid state '{state}'"
        except requests.RequestException as e:
            assert False, f"RequestException raised for alerts invalid state '{state}': {e}"

    # Interactive chat commands endpoint (assuming a POST to /chat with user input text)
    chat_url = f"{BASE_URL}/chat"
    invalid_chat_inputs = [
        "Atlantis",
        "Gotham City",
        "12345",
        "",
        None,
        "/forecast imaginaryplace",
        "Weather in Middle Earth",
    ]
    for user_input in invalid_chat_inputs:
        payload = {"message": user_input} if user_input is not None else {}
        try:
            response = requests.post(
                chat_url, json=payload, headers=HEADERS, timeout=TIMEOUT
            )
            # Expect 400 or 422 or a valid 200 with error message in content
            if response.status_code in (400, 422):
                try:
                    json_resp = response.json()
                except Exception:
                    assert False, f"No JSON response for chat input '{user_input}' with status {response.status_code}"
                assert (
                    "error" in json_resp or "message" in json_resp
                ), f"Expected error message in chat response for input '{user_input}'"
                guidance = json_resp.get("error") or json_resp.get("message")
                assert (
                    "invalid" in guidance.lower()
                    or "unsupported" in guidance.lower()
                    or "could not recognize" in guidance.lower()
                    or "no location" in guidance.lower()
                    or "please" in guidance.lower()
                ), f"Expected user guidance for chat input '{user_input}'"
            elif response.status_code == 200:
                try:
                    json_resp = response.json()
                except Exception:
                    assert False, f"No JSON response for chat input '{user_input}' with status 200"
                # Check if the response indicates error or guidance message
                text = json_resp.get("response") or json_resp.get("message") or ""
                assert (
                    "invalid" in text.lower()
                    or "unsupported" in text.lower()
                    or "sorry" in text.lower()
                    or "could not recognize" in text.lower()
                    or "please" in text.lower()
                ), f"Expected user guidance or error message in chat response for input '{user_input}'"
            else:
                assert False, f"Unexpected status code {response.status_code} for chat input '{user_input}'"
        except requests.RequestException as e:
            assert False, f"RequestException raised for chat input '{user_input}': {e}"

test_handle_invalid_location_inputs_gracefully()