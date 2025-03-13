# my-facade-api/src/domain/collateral/models.py
from typing import List, Dict, Optional, Union
from pydantic import BaseModel, EmailStr, create_model, Field
from src.adapters.api_client import make_api_request
import enum
import yaml

def generate_collateral_models(dynamic=False):
    """Generates Pydantic models dynamically based on the API response."""
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
                collateral_props = data_properties["collaterals"]["items"]["properties"]
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
                                        "schema": CollateralPatchSuccess.schema()
                                    }
                                }
                            },
                            "400": {
                                "description": "Failed patch",
                                "content": {
                                    "application/json": {
                                        "schema": CollateralPatchFailure.schema()
                                    }
                                }
                            }
                        }
                    }
                },
                "/collateral/fields": {
                    "get": {
                        "summary": "Get Collateral Fields",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "type": "string"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/collateral/openapi.yaml": {
                    "get": {
                        "summary": "Get OpenAPI Spec",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "text/yaml": {}
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "CollateralOverview": {
                        "type": "object",
                        "properties": {
                            "meta": {
                                "$ref": "#/components/schemas/MetaData"
                            },
                            "data": {
                                "$ref": "#/components/schemas/CollateralData"
                            }
                        }
                    },
                    "MetaData": {
                        "type": "object",
                        "properties": {
                            "updatedBy": {
                                "type": "string",
                                "format": "email"
                            }
                        }
                    },
                    "CollateralData": {
                        "type": "object",
                        "properties": {
                            "transaction": {
                                "$ref": "#/components/schemas/TransactionData"
                            },
                            "collaterals": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/CollateralItem"
                                }
                            }
                        }
                    },
                    "TransactionData": {
                        "type": "object",
                        "properties": {
                            "type": "object"
                        }
                    },
                    "CollateralItem": {
                        "type": "object",
                        "properties": {
                            "type": "object"
                        }
                    },
                    "CollateralPatchSuccess": {
                        "type": "object",
                        "properties": {
                            "meta": {
                                "type": "object"
                            },
                            "data": {
                                "type": "object"
                            }
                        }
                    },
                    "CollateralPatchFailure": {
                        "type": "object",
                        "properties": {
                            "meta": {
                                "type": "object"
                            },
                            "data": {
                                "type": "object"
                            }
                        }
                    }
                }
            }
        }
        return (
            TransactionData,
            CollateralItem,
            MetaData,
            CollateralData,
            CollateralOverview,
            CollateralPatchSuccess,
            CollateralPatchFailure,
        )


def map_field_type(field_type: str, field_info: dict):
    """Maps API field types to Python types, handling enums and required fields."""
    if "enum" in field_info:
        enum_name = field_info.get("field", "DynamicEnum").replace(" ", "")  # generate enum name
        enum_values = {val: val for val in field_info["enum"]}
        DynamicEnum = enum.Enum(enum_name, enum_values)
        return Optional[DynamicEnum]
    elif field_type == "string":
        return Optional[str]
    elif field_type == "integer":
        return Optional[int]
    elif field_type == "boolean":
        return Optional[bool]
    elif field_type == "array":
        return Optional[List[dict]]
    elif field_type == "object":
        return Optional[dict]
    else:
        return Optional[str]  # Default to string
