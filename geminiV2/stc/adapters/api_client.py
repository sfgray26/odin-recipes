# my-facade-api/src/adapters/api_client.py
import requests
import os
import json
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

TOKEN_URL = os.getenv("TOKEN_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SCOPE = os.getenv("SCOPE")
TARGET_API_URL = os.getenv("TARGET_API_URL")
PROXIES = {
    "http": os.getenv("PROXY_HTTP"),
    "https": os.getenv("PROXY_HTTPS"),
}


def get_bearer_token():
    """Retrieves a bearer token from the authentication server."""
    try:
        data = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": SCOPE,
        }
        response = requests.post(TOKEN_URL, data=data, proxies=PROXIES)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("data").get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve bearer token")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        raise HTTPException(status_code=500, detail="Error decoding token response")
    except KeyError as e:
        print(f"KeyError: {e}. Check token response format.")
        raise HTTPException(status_code=500, detail="Invalid token response format")


def make_api_request(endpoint: str, method: str = "GET", params: dict = None, data: dict = None):
    """Makes a request to the target API with the given endpoint and parameters."""
    token = get_bearer_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{TARGET_API_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, proxies=PROXIES)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, params=params, proxies=PROXIES)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data, params=params, proxies=PROXIES)
        else:
            raise HTTPException(status_code=405, detail=f"Method '{method}' not allowed")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        try:
            error_message = e.response.json()
        except json.JSONDecodeError:
            error_message = str(e)
        raise HTTPException(status_code=e.response.status_code, detail=error_message)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to API: {e}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Error decoding API response")
