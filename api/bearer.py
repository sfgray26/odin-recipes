# my-facade-api/tests/test_api_client.py
import unittest
from src.adapters.api_client import get_bearer_token
import os
from dotenv import load_dotenv

load_dotenv()

class TestApiClient(unittest.TestCase):

    def setUp(self):
        # Ensure that the environment variables are set.
        # This is important for the test to run correctly.
        self.token_url = os.environ.get("TOKEN_URL")
        self.client_id = os.environ.get("CLIENT_ID")
        self.client_secret = os.environ.get("CLIENT_SECRET")
        self.scope = os.environ.get("SCOPE")

        self.assertIsNotNone(self.token_url, "TOKEN_URL environment variable is not set.")
        self.assertIsNotNone(self.client_id, "CLIENT_ID environment variable is not set.")
        self.assertIsNotNone(self.client_secret, "CLIENT_SECRET environment variable is not set.")
        self.assertIsNotNone(self.scope, "SCOPE environment variable is not set.")

    def test_get_bearer_token_success(self):
        token = get_bearer_token()
        self.assertIsNotNone(token, "Failed to retrieve bearer token.")
        self.assertTrue(isinstance(token, str), "Token is not a string.")
        self.assertTrue(len(token) > 0, "Token is empty.")

    def test_get_bearer_token_failure_invalid_credentials(self):
        # Temporarily modify environment variables to simulate invalid credentials
        original_client_id = os.environ.get("CLIENT_ID")
        os.environ["CLIENT_ID"] = "invalid_client_id"

        token = get_bearer_token()
        self.assertIsNone(token, "Token should be None with invalid credentials.")

        # Restore the original environment variable
        os.environ["CLIENT_ID"] = original_client_id

    def test_get_bearer_token_failure_invalid_url(self):
        # Temporarily modify environment variables to simulate invalid token URL
        original_token_url = os.environ.get("TOKEN_URL")
        os.environ["TOKEN_URL"] = "http://invalid_url"

        token = get_bearer_token()
        self.assertIsNone(token, "Token should be None with invalid URL.")

        # Restore the original environment variable
        os.environ["TOKEN_URL"] = original_token_url

if __name__ == '__main__':
    unittest.main()

Key Improvements and Explanations:
 * Environment Variable Checks in setUp():
   * The setUp() method now checks if the required environment variables (TOKEN_URL, CLIENT_ID, CLIENT_SECRET, SCOPE) are set.
   * If any of these variables are missing, the test will fail early, providing a clear error message.
   * This ensures that the test doesn't proceed with invalid configurations.
 * test_get_bearer_token_success():
   * This test verifies that the get_bearer_token() function returns a valid token when the credentials and URL are correct.
   * It asserts that the token is not None, is a string, and is not empty.
 * test_get_bearer_token_failure_invalid_credentials():
   * This test simulates a scenario where the client ID is invalid.
   * It temporarily modifies the CLIENT_ID environment variable, calls get_bearer_token(), and asserts that the function returns None.
   * It then restores the original CLIENT_ID to avoid affecting other tests.
 * test_get_bearer_token_failure_invalid_url():
   * This test simulates a scenario where the token URL is invalid.
   * It temporarily modifies the TOKEN_URL environment variable, calls get_bearer_token(), and asserts that the function returns None.
   * It then restores the original TOKEN_URL.
 * Clear Error Messages:
   * The assertions now include descriptive error messages to help you understand the cause of test failures.
How to Run the Tests:
 * Make sure you have your virtual environment activated and the required dependencies installed.
 * Run python -m unittest tests/test_api_client.py from your project root.
Important Notes:
 * Environment Variables: Ensure that your .env file is correctly configured with the necessary credentials and URLs.
 * Token Endpoint: The tests assume that your token endpoint will return a 400 or 401 status code when the credentials are invalid. Adjust the assertions if your endpoint behaves differently.
 * Error Handling: The get_bearer_token() function in api_client.py should handle potential exceptions (e.g., network errors, invalid JSON) gracefully.
 * https://github.com/davitkv8/BOG-TBC-PAYMENT-AND-ACCOUNTING
