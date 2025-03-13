# my-facade-api/src/domain/collateral/services.py
from src.adapters.api_client import make_api_request
from fastapi import HTTPException
from typing import Tuple, Dict, Any

def get_collateral_overview(location_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Retrieves the collateral overview for a specific location.
    """
    try:
        response = make_api_request(f"/collateralOverview/{location_id}")
        return response, 200
    except HTTPException as e:
        return {"error": e.detail}, e.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def patch_collateral_overview(location_id: int, data: dict) -> Tuple[Dict[str, Any], int]:
    """
    Updates the collateral overview for a specific location.
    """
    try:
        response = make_api_request(f"/collateralOverview/{location_id}", method="PATCH", data=data)
        return response, 200
    except HTTPException as e:
        return {"error": e.detail}, e.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def get_collateral_fields() -> Tuple[Dict[str, Any], int]:
    """
    Retrieves the field definitions for collateral data.
    """
    try:
        response = make_api_request("/collateralOverview/fields")
        return response, 200
    except HTTPException as e:
        return {"error": e.detail}, e.status_code
    except Exception as e:
        return {"error": str(e)}, 500
