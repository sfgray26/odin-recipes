import asyncio
import time
from fastapi import APIRouter, HTTPException
from pydantic import create_model
from .client import make_request_with_retry
from .auth import get_access_token
from .config import API_BASE_URL, SCHEMA_CACHE_TTL, SERVICE_TYPE_CACHE_TTL

router = APIRouter()

# Caching state
schema_cache = {"data": None, "expires_at": 0}
service_type_cache = {"data": None, "expires_at": 0}
schema_lock = asyncio.Lock()
service_type_lock = asyncio.Lock()

# ================== SCHEMA RETRIEVAL ==================
@router.get("/service-request/schema")
async def get_service_request_schema():
    async with schema_lock:
        if schema_cache["data"] and time.time() < schema_cache["expires_at"]:
            return schema_cache["data"]

        token = await get_access_token()
        url = f"{API_BASE_URL}/serviceRequest/fields"
        headers = {"Authorization": f"Bearer {token}"}
        response = await make_request_with_retry(url, headers)

        schema = response.json().get("data", {}).get("model", {}).get("jsonSchema", {})
        if not schema:
            raise HTTPException(status_code=500, detail="Failed to retrieve schema")

        schema_cache["data"] = schema
        schema_cache["expires_at"] = time.time() + SCHEMA_CACHE_TTL
        return schema

# ================== SERVICE TYPES RETRIEVAL ==================
@router.get("/service-types")
async def get_service_types():
    async with service_type_lock:
        if service_type_cache["data"] and time.time() < service_type_cache["expires_at"]:
            return service_type_cache["data"]

        token = await get_access_token()
        url = f"{API_BASE_URL}/utility/serviceTypes"
        headers = {"Authorization": f"Bearer {token}"}
        response = await make_request_with_retry(url, headers)

        service_types = response.json().get("data", [])
        if not service_types:
            raise HTTPException(status_code=500, detail="Failed to retrieve service types")

        service_type_cache["data"] = [st.get("serviceType") for st in service_types]
        service_type_cache["expires_at"] = time.time() + SERVICE_TYPE_CACHE_TTL
        return service_type_cache["data"]

# ================== SERVICE REQUEST CREATION ==================
@router.post("/service-request")
async def create_service_request(request_body: dict):
    schema = await get_service_request_schema()
    service_types = await get_service_types()

    # Generate dynamic models
    CollateralModel = create_model("CollateralModel", **{
        "serviceType": (str, ...),
        "value": (float, None)
    })

    try:
        for collateral in request_body["data"]["collaterals"]:
            for service in collateral["services"]:
                if service["serviceType"] not in service_types:
                    raise ValueError(f"Invalid service type: {service['serviceType']}")
            CollateralModel(**collateral)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    token = await get_access_token()
    url = f"{API_BASE_URL}/serviceRequest/form"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = await make_request_with_retry(url, headers, method="POST", data=request_body)

    if response.status_code == 201:
        return response.json()["data"]
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())