# my-facade-api/src/adapters/api_client.py
import requests
import os
import json
from dotenv import load_dotenv

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
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    except KeyError as e:
        print(f"KeyError: {e}. Check token response format.")
        return None

def make_api_request(endpoint, params=None, method='GET', data=None):
    token = get_bearer_token()
    if not token:
        return {"error": "Failed to retrieve bearer token"}, 401

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{TARGET_API_URL}{endpoint}"

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, proxies=PROXIES)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, params=params, proxies=PROXIES)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, params=params, proxies=PROXIES)
        else:
            return {"error": "Invalid method"}, 400

        response.raise_for_status()
        response_json = response.json()
        return response_json, response.status_code
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, response.status_code if 'response' in locals() else 500
    except json.JSONDecodeError as e:
        return {"error": f"JSON Decode Error: {e}"}, 500
