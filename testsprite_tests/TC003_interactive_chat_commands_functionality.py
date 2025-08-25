import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}


def test_interactive_chat_commands_functionality():
    commands = {
        "/help": "usage_instructions",
        "/tools": "available_features",
        "/quit": "exit_message"
    }

    for command, expected_key in commands.items():
        try:
            response = requests.post(
                f"{BASE_URL}/chat/command",
                json={"command": command},
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            assert False, f"Request for command '{command}' failed: {e}"

        json_resp = response.json()
        # Validate response contains expected keys depending on command
        assert isinstance(json_resp, dict), f"Response for command '{command}' is not a JSON object"
        assert expected_key in json_resp, f"Response for command '{command}' missing expected key '{expected_key}'"
        assert json_resp[expected_key], f"The '{expected_key}' value for command '{command}' is empty or falsy"

        # Additional checks for /quit command to confirm correct action
        if command == "/quit":
            assert json_resp.get("exit") is True or json_resp.get("exit") == "true", "/quit command should indicate exit action"


test_interactive_chat_commands_functionality()