# my-facade-api/app.py
import os
from flask import Flask
from dotenv import load_dotenv

from src.presentation.oauth_blueprint import oauth_bp
from src.presentation.collateral_blueprint import collateral_bp
from src.presentation.loan_info_blueprint import loan_info_bp
from src.presentation.service_request_blueprint import service_request_bp
from src.presentation.utilities_blueprint import utilities_bp
from src.presentation.webhooks_blueprint import webhooks_bp
from src.presentation.data_capture_blueprint import data_capture_bp

load_dotenv()

app = Flask(__name__)

app.register_blueprint(oauth_bp)
app.register_blueprint(collateral_bp)
app.register_blueprint(loan_info_bp)
app.register_blueprint(service_request_bp)
app.register_blueprint(utilities_bp)
app.register_blueprint(webhooks_bp)
app.register_blueprint(data_capture_blueprint)

if __name__ == '__main__':
    app.run(debug=True)

# my-facade-api/.env
# TOKEN_URL=YOUR_TOKEN_ENDPOINT_URL
# CLIENT_ID=YOUR_CLIENT_ID
# CLIENT_SECRET=YOUR_CLIENT_SECRET
# SCOPE=YOUR_DESIRED_SCOPE
# TARGET_API_URL=https://api.lightboxre.com/v1/los
# PROXY_HTTP=http://your_proxy_address:your_proxy_port
# PROXY_HTTPS=https://your_proxy_address:your_proxy_port

# my-facade-api/.gitignore
# venv/
# __pycache__/
# *.pyc
# .env

# my-facade-api/requirements.txt
# Flask
# requests
# python-dotenv
# pydantic
# pyyaml

# my-facade-api/src/adapters/api_client.py
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = os.environ.get("TOKEN_URL")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
SCOPE = os.environ.get("SCOPE")
TARGET_API_URL = os.environ.get("TARGET_API_URL")
PROXIES = {
    "http": os.environ.get("PROXY_HTTP"),
    "https": os.environ.get("PROXY_HTTPS"),
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
        return token_data.get("access_token")
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
        return None, 500

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    full_target_url = f"{TARGET_API_URL}{endpoint}"

    try:
        if method == 'GET':
            response = requests.get(full_target_url, headers=headers, params=params, proxies=PROXIES)
        elif method == 'POST':
            response = requests.post(full_target_url, headers=headers, json=data, proxies=PROXIES)
        elif method == 'PUT':
            response = requests.put(full_target_url, headers=headers, json=data, proxies=PROXIES)
        elif method == 'PATCH':
            response = requests.patch(full_target_url, headers=headers, json=data, proxies=PROXIES)
        elif method == 'DELETE':
            response = requests.delete(full_target_url, headers=headers, proxies=PROXIES)
        else:
            return None, 400

        response.raise_for_status()
        return response.json(), 200

    except requests.exceptions.RequestException as e:
        return None, 500
    except json.JSONDecodeError as e:
        return None, 500

# my-facade-api/src/domain/collateral/models.py
from typing import List, Dict, Optional, Union
from pydantic import BaseModel, EmailStr, create_model
from src.adapters.api_client import make_api_request

def generate_collateral_models():
    fields_data, status_code = make_api_request('/collateralOverview/fields')
    if status_code != 200:
        print("Error fetching fields data. Using default models.")
        return DefaultModels # Return default models if fetching fails

    field_definitions = {}
    if fields_data and isinstance(fields_data, list):
        for field in fields_data:
            field_name = field['name']
            field_type = field['type']

            if field_type == 'string':
                python_type = Optional[str]
            elif field_type == 'integer':
                python_type = Optional[int]
            elif field_type == 'boolean':
                python_type = Optional[bool]
            elif field_type == "array":
                python_type = Optional[List[dict]]
            elif field_type == "object":
                python_type = Optional[dict]
            else:
                python_type = Optional[str]

            field_definitions[field_name] = (python_type, None)

    TransactionData = create_model('TransactionData', **field_definitions)
    CollateralItem = create_model('CollateralItem', **field_definitions)

    class MetaData(BaseModel):
        updatedBy: EmailStr

    class CollateralData(BaseModel):
        transaction: TransactionData
        collaterals: List[CollateralItem]

    class CollateralOverview(BaseModel):
        meta: MetaData
        data: CollateralData

    class CollateralPatchSuccess(BaseModel):
        meta: Dict
        data: Dict

    class CollateralPatchFailure(BaseModel):
        meta: Dict
        data: Dict = {}

    return TransactionData, CollateralItem, MetaData, CollateralData, CollateralOverview, CollateralPatchSuccess, CollateralPatchFailure

TransactionData, CollateralItem, MetaData, CollateralData, CollateralOverview, CollateralPatchSuccess, CollateralPatchFailure = generate_collateral_models()

# my-facade-api/src/domain/collateral/services.py
from src.adapters.api_client import make_api_request
from .models import CollateralOverview, CollateralPatchSuccess, CollateralPatchFailure

def get_collateral_overview(location_id):
    result, status_code = make_api_request(f'/loan/information/collateralOverview/{location_id}')
    if status_code == 200:
        try:
            return CollateralOverview(**result), status_code
        except Exception as e:
            print(f"Error parsing CollateralOverview: {e}")
            return None, 500
    return None, status_code

def patch_collateral_overview(location_id, data):
    result, status_code = make_api_request(f'/collateralOverview/{location_id}', method='PATCH', data=data)
    if status_code == 200:
        try:
            return CollateralPatchSuccess(**result), status_code
        except Exception as e:
            print(f"Error parsing CollateralPatchSuccess: {e}")
            return None, 500
    elif status_code == 400:
        try:
            return CollateralPatchFailure(**result), status_code
        except Exception as e:
            print(f"Error parsing CollateralPatchFailure: {e}")
            return None, 500
    return None, status_code

def get_collateral_fields():
    result, status_code = make_api_request('/collateralOverview/fields')
    return result, status_code

# my-facade-api/src/presentation/collateral_blueprint.py
from

 * https://github.com/HozefaMJ/datafeed-fa
