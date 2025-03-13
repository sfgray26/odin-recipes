# my-facade-api/src/domain/collateral/models.py
from typing import List, Dict, Optional, Union
from pydantic import BaseModel, EmailStr, create_model, Field
from src.adapters.api_client import make_api_request
import enum
import yaml

def generate_collateral_models(dynamic=False):
    if dynamic:
        fields_data, status_code = make_api_request('/collateralOverview/fields')
        if status_code != 200:
            print("Error fetching fields data. Using default models.")
            return {}

        transaction_definitions = {}
        collateral_definitions = {}

        if (
            fields_data
            and isinstance(fields_data, dict)
            and "data" in fields_data
            and "model" in fields_data["data"]
            and "jsonSchema" in fields_data["data"]["model"]
            and "properties" in fields_data["data"]["model"]["jsonSchema"]
            and "data" in fields_data["data"]["model"]["jsonSchema"]["properties"]
            and "properties" in fields_data["data"]["model"]["jsonSchema"]["properties"]["data"]
        ):
            data_properties = fields_data["data"]["model"]["jsonSchema"]["properties"]["data"]["properties"]

            # Extract Transaction Fields
            if "transaction" in data_properties and "properties" in data_properties["transaction"]:
                transaction_props = data_properties["transaction"]["properties"]
                for field_name, field_info in transaction_props.items():
                    if "type" in field_info:
                        field_type = field_info["type"]
                        python_type = map_field_type(field_type, field_info)  # Use helper function
                        transaction_definitions[field_name] = (python_type, None)

            # Extract Collateral Fields
            if "collaterals" in data_properties and "items" in data_properties["collaterals"] and "properties" in data_properties["collaterals"]["items"]:
                collateral_props = data_properties["collaterals"]["items"]["properties"] # corrected line
                for field_name, field_info in collateral_props.items():
                    if "type" in field_info:
                        field_type = field_info["type"]
                        python_type = map_field_type(field_type, field_info)  # Use helper function
                        collateral_definitions[field_name] = (python_type, None)

        TransactionData = create_model("TransactionData", **transaction_definitions)
        CollateralItem = create_model("CollateralItem", **collateral_definitions)

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
            data: Dict

        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Collateral Overview API",
                "version": "1.0.0"
            },
            "paths": {
                "/collateral/collateralOverview/{location_id}": {
                    "get": {
                        "summary": "Get Collateral Overview",
                        "parameters": [
                            {
                                "name": "location_id",
                                "in": "path",
                                "required": True,
                                "schema": {
                                    "type": "integer"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": CollateralOverview.schema()
                                    }
                                }
                            }
                        }
                    },
                    "patch": {
                        "summary": "Patch Collateral Overview",
                        "parameters": [
                            {
                                "name": "location_id",
                                "in": "path",
                                "required": True,
                                "schema": {
                                    "type": "integer"
                                }
                            }
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": CollateralOverview.schema()
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful patch",
                                "content": {
                                    "application/json": {
                                        "
