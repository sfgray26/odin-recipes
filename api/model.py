Okay, thanks for providing the additional context. It's clear now that the API response is structured with different sections for "transaction" and "collateral" data, and these sections are nested within the larger JSON schema.
To handle this correctly, you'll need to modify your generate_collateral_models function to:
 * Extract Transaction Fields:
   * Navigate to the correct section of the JSON response to extract the field definitions for TransactionData.
 * Extract Collateral Fields:
   * Navigate to the correct section of the JSON response to extract the field definitions for CollateralItem.
Here's an updated version of the generate_collateral_models function that incorporates these changes:
# my-facade-api/src/domain/collateral/models.py
from typing import List, Dict, Optional, Union
from pydantic import BaseModel, EmailStr, create_model
from src.adapters.api_client import make_api_request

def generate_collateral_models():
    fields_data, status_code = make_api_request('/collateralOverview/fields')
    if status_code != 200:
        print("Error fetching fields data. Using default models.")
        return DefaultModels  # Return default models if fetching fails

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
                    python_type = map_field_type(field_type)  # Use helper function
                    transaction_definitions[field_name] = (python_type, None)

        # Extract Collateral Fields
        if "collateral" in data_properties and "properties" in data_properties["collateral"]:
            collateral_props = data_properties["collateral"]["properties"]
            for field_name, field_info in collateral_props.items():
                if "type" in field_info:
                    field_type = field_info["type"]
                    python_type = map_field_type(field_type)  # Use helper function
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
        data: Dict = {}

    return (
        TransactionData,
        CollateralItem,
        MetaData,
        CollateralData,
        CollateralOverview,
        CollateralPatchSuccess,
        CollateralPatchFailure,
    )


def map_field_type(field_type: str):
    """Maps API field types to Python types."""
    if field_type == "string":
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

Key Changes:
 * Separate Extraction:
   * The code now separately extracts field definitions for transaction and collateral by navigating to the appropriate sections within the JSON response.
 * Helper Function:
   * A helper function map_field_type is introduced to improve code readability and maintainability.
   * This function maps the API field types to Python types, making the main logic cleaner.
 * Model Creation:
   * TransactionData and CollateralItem are now created using the extracted transaction_definitions and collateral_definitions, respectively.
 * Tuple Unpacking:
   * The return statement now explicitly names the variables in the tuple.
Important Notes:
 * Further Validation: You may need to add more checks and error handling to handle cases where the API response structure deviates from the expected format.
 * Complete Structure: Ensure that you have a complete understanding of the API's response structure to handle all possible scenarios.
 * Testing: Thoroughly test your code after making these changes to ensure that it's working as expected.
