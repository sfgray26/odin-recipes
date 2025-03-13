# my-facade-api/src/presentation/collateral_router.py
from fastapi import APIRouter, HTTPException, Depends
from src.domain.collateral.services import get_collateral_overview, patch_collateral_overview, get_collateral_fields
from src.domain.collateral.models import CollateralOverview, generate_collateral_models
from typing import Annotated, Optional
from fastapi.responses import JSONResponse
import yaml
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import random
import string

router = APIRouter()

# Generate models dynamically
(
    TransactionData,
    CollateralItem,
    MetaData,
    CollateralData,
    CollateralOverview,
    CollateralPatchSuccess,
    CollateralPatchFailure,
) = generate_collateral_models(dynamic=True)


@router.get("/collateralOverview/{location_id}")
async def read_collateral_overview(location_id: int):
    """
    Retrieves the collateral overview for a specific location.
    """
    result, status_code = get_collateral_overview(location_id)
    if status_code == 200:
        try:
            collateral_overview = CollateralOverview(**result)
            return jsonable_encoder(collateral_overview)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=status_code, detail=result)


@router.patch("/collateralOverview/{location_id}")
async def update_collateral_overview(location_id: int, collateral_overview: CollateralOverview):
    """
    Updates the collateral overview for a specific location.
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
    """
    result, status_code = get_collateral_fields()
    if status_code == 200:
        return result
    raise HTTPException(status_code=status_code, detail=result)


@router.get("/openapi.yaml", response_class=fastapi.responses.PlainTextResponse)
async def get_openapi_spec():
    """
    Generates the OpenAPI specification for the collateral API.
    """
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title="Collateral Overview API",
        version="1.0.0",
        routes=app.routes,
    )
    yaml_data = yaml.dump(openapi_schema)
    return yaml_data


# Mock data generation
def generate_mock_data(model):
    """Generates mock data for a given Pydantic model."""
    mock_data = {}
    for field_name, field_type in model.__fields__.items():
        if field_type.type_ == str:
            mock_data[field_name] = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        elif field_type.type_ == int:
            mock_data[field_name] = random.randint(1, 100)
        elif field_type.type_ == bool:
            mock_data[field_name] = random.choice([True, False])
        elif hasattr(field_type.type_, "__origin__") and field_type.type_.__origin__ == list:
            mock_data[field_name] = [generate_mock_data(field_type.type_.__args__[0])]
        elif issubclass(field_type.type_, BaseModel):
            mock_data[field_name] = generate_mock_data(field_type.type_)
        elif hasattr(field_type.type_, "__members__"): #handle enums
            mock_data[field_name] = random.choice(list(field_type.type_.__members__.values()))
        else:
            mock_data[field_name] = None
    return mock_data

# Service request endpoint
@router.post("/v1/los/serviceRequest/form")
async def create_service_request(processAsWarnings: Optional[bool] = True):
    """Creates a mock service request and returns the generated data."""
    mock_meta = {
        "requestedBy": "mock@example.com",
        "createdBy": "mock@example.com",
        "cabinet": "Mock Cabinet",
        "currency": "USD",
        "srfAction": "DRAFT",
        "processAsWarnings": processAsWarnings,
    }
    mock_transaction = generate_mock_data(TransactionData)
    mock_services = [
        {
            "serviceType": "MockAppraisal",
            "displayName": "Mock Appraisal Service",
            "featureID": random.randint(100, 200),
            "featureName": "Mock Appraisal",
        }
        for _ in range(random.randint(1, 2))
    ]
    mock_collaterals = [
        {
            **generate_mock_data(CollateralItem),
            "services": mock_services,
        }
        for _ in range(random.randint(1, 3))
    ]
    mock_data = {
        "transaction": mock_transaction,
        "collaterals": mock_collaterals,
    }
    mock_response = {
        "meta": {
            "date": "2024-01-27T12:00:00Z",  # Mock date
            "function": "create",
            "responseCode": 201,
            "responseID": "mock-uuid",  # Mock UUID
            "success": True,
            "warnings": [],
        },
        "data": {
            "serviceRequestID": random.randint(100000, 200000),
            "locationID": [random.randint(200000, 300000) for _ in range(random.randint(1, 2))],
        },
    }
    return mock_response
