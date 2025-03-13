# my-facade-api/src/presentation/collateral_router.py
from fastapi import APIRouter, HTTPException, Depends
from src.domain.collateral.services import get_collateral_overview, patch_collateral_overview, get_collateral_fields
from src.domain.collateral.models import CollateralOverview
from typing import Annotated
from fastapi.responses import JSONResponse
import yaml
from fastapi.encoders import jsonable_encoder

router = APIRouter()


@router.get("/collateralOverview/{location_id}")
async def read_collateral_overview(location_id: int):
    """
    Retrieves the collateral overview for a specific location.

    Args:
        location_id (int): The ID of the location.

    Returns:
        CollateralOverview: The collateral overview data.

    Raises:
        HTTPException:
            - 404: If the collateral overview is not found.
            - 500: If an error occurs while retrieving the data.
    """
    result, status_code = get_collateral_overview(location_id)
    if status_code == 200:
        try:
            collateral_overview = CollateralOverview(**result)  # Validate and parse
            return jsonable_encoder(collateral_overview)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))  # Handle validation errors
    raise HTTPException(status_code=status_code, detail=result)


@router.patch("/collateralOverview/{location_id}")
async def update_collateral_overview(location_id: int, collateral_overview: CollateralOverview):
    """
    Updates the collateral overview for a specific location.

    Args:
        location_id (int): The ID of the location.
        collateral_overview (CollateralOverview): The updated collateral overview data.

    Returns:
        CollateralPatchSuccess: The result of the update operation.

    Raises:
        HTTPException:
            - 400: If the request data is invalid.
            - 500: If an error occurs while updating the data.
    """
    data = collateral_overview.dict()
    result, status_code = patch_collateral_overview(location_id, data)
    if status_code == 200:
        return result
    raise HTTPException(status_code=status_code, detail=result)


@router.get("/fields")
async def read_collateral_fields():
    """
    Retrieves the field definitions for collateral data.

    Returns:
        dict: The field definitions.

    Raises:
        HTTPException:
            - 500: If an error occurs while retrieving the field definitions.
    """
    result, status_code = get_collateral_fields()
    if status_code == 200:
        return result
    raise HTTPException(status_code=status_code, detail=result)


@router.get("/openapi.yaml", response_class=fastapi.responses.PlainTextResponse)
async def get_openapi_spec():
    """
    Generates the OpenAPI specification for the collateral API.

    Returns:
        PlainTextResponse: The OpenAPI specification in YAML format.
    """
    from
