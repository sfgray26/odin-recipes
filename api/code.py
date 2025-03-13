# my-facade-api/src/presentation/collateral_blueprint.py
from flask import Blueprint, jsonify, request
from src.domain.collateral.services import get_collateral_overview, patch_collateral_overview, get_collateral_fields
from pydantic import ValidationError
import yaml
from src.domain.collateral.models import TransactionData, CollateralItem, CollateralOverview, CollateralPatchSuccess, CollateralPatchFailure

collateral_bp = Blueprint('collateral', __name__, url_prefix='/collateral')

@collateral_bp.route('/collateralOverview/<int:location_id>', methods=['GET'])
def get_collateral_overview_endpoint(location_id):
    result, status_code = get_collateral_overview(location_id)
    if status_code == 200:
        return jsonify(result.dict()), status_code
    return jsonify(result), status_code

@collateral_bp.route('/collateralOverview/<int:location_id>', methods=['PATCH'])
def patch_collateral_overview_endpoint(location_id):
    data = request.get_json()
    result, status_code = patch_collateral_overview(location_id, data)
    if status_code == 200:
        return jsonify(result.dict()), status_code
    return jsonify(result), status_code

@collateral_bp.route('/fields', methods=['GET'])
def get_collateral_fields_endpoint():
    result, status_code = get_collateral_fields()
    return jsonify(result), status_code

@collateral_bp.route('/openapi.yaml', methods=['GET'])
def get_openapi_spec():
    spec = generate_dynamic_openapi_spec()
    return yaml.dump(spec, sort_keys=False, indent=2), 200, {'Content-Type': 'text/yaml'} #Added indent and sort keys

def generate_dynamic_openapi_spec():
    transaction_properties = {field_name: {"type": get_openapi_type(field_type)} for field_name, (field_type, _) in TransactionData.__fields__.items()}
    collateral_item_properties = {field_name: {"type": get_openapi_type(field_type)} for field_name, (field_type, _) in CollateralItem.__fields__.items()}

    spec = {
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
                                    "schema": {
                                        "$ref": "#/components/schemas/CollateralOverview"
                                    }
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
                                "schema": {
                                    "$ref": "#/components/schemas/CollateralOverview"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful patch",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CollateralPatchSuccess"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Failed patch",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CollateralPatchFailure"
                                    }
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
                                                "type": {
                                                    "type": "string"
                                                }
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
                    "properties": transaction_properties
                },
                "CollateralItem": {
                    "type": "object",
                    "properties": collateral_item_properties
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
    return spec

def get_openapi_type(python_type):
    if hasattr(python_type, '__origin__'):
        if python_type.__origin__ is list:
            return "array"
        elif python_type.__origin__ is dict:
            return "object"
        elif python_type.__origin__ is Union:
            return "string" #handle unions as strings for now.
    if python_type is str or python_type is type(None) or python_type is Optional[str] :
        return "string"
    elif python_type is int or python_type is type(None) or python_type is Optional[int]:
        return "integer"
    elif python_type is bool or python_type is type(None) or python_type is Optional[bool]:
        return "boolean"
    else:
        return "string"
