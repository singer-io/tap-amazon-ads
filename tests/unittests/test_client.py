import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import requests
from tap_amazon_ads.client import Client, raise_for_error
from tap_amazon_ads.exceptions import (ERROR_CODE_EXCEPTION_MAPPING,
                                       Amazon_AdsError,
                                       Amazon_AdsUnauthorizedError,
                                       Amazon_AdsBadRequestError,
                                       Amazon_AdsRateLimitError,
                                       Amazon_AdsInternalServerError)
from requests.exceptions import ConnectionError, Timeout, ChunkedEncodingError


class Mockresponse:
    """Mock response object class."""
    def __init__(self, status_code, json, raise_error, headers={}, text=None):
        self.status_code = status_code
        self.raise_error = raise_error
        self.text = json
        self.headers = headers

    def raise_for_status(self):
        if not self.raise_error:
            return self.status_code

        raise requests.HTTPError("Sample message")

    def json(self):
        """Response JSON method."""
        return self.text


def get_response(status_code, json={}, headers={}, raise_error=False):
    """Returns required mock response."""
    return Mockresponse(status_code, json, raise_error, headers)


class TestRaiseForError(unittest.TestCase):
    """
    Unit tests for the `raise_for_error` function in the tap_amazon_ads.client module.

    This test class verifies that:
      - No exception is raised for successful HTTP status codes (200, 201, 204).
      - Appropriate exceptions are raised for various error status codes.
      - Error messages are constructed correctly from the response JSON.
      - Default error messages are used when response details are missing.

    The tests use mocked `requests.Response` objects to simulate different API responses
    without making actual HTTP requests.
    """
    def test_success_status_does_not_raise(self):
        """
        Test that `raise_for_error` does not raise an exception for successful HTTP status codes.
        """
        for code in [200, 201, 204]:
            with self.subTest(status_code=code):
                response = get_response(code, {"message": "OK"})
                try:
                    raise_for_error(response)
                except Exception as e:
                    self.fail(f"raise_for_error raised an exception on status {code}: {e}")

    def test_error_with_code_key_raises_mapped_exception(self):
        """
        Test that `raise_for_error` raises the correct mapped exception when the response JSON includes a 'code' key.
        Simulates an error response (e.g. HTTP 400 or 401) with a JSON body containing a 'code' and 'details' field.
        """
        response = get_response(400, {"code": "BadRequest", "details": "Invalid input"})
        # Assertions
        with self.assertRaises(Amazon_AdsBadRequestError) as context:
            raise_for_error(response)
        self.assertIn("HTTP-error-code: 400", str(context.exception))

    def test_error_with_message_key_raises_mapped_exception(self):
        """
        Test that `raise_for_error` raises the correct mapped exception when the response JSON contains a 'message' key but no 'code'.
        """
        response = get_response(401, {"message": "Unauthorized access"})
        # Assertions
        with self.assertRaises(Amazon_AdsUnauthorizedError) as context:
            raise_for_error(response)
        self.assertIn("Unauthorized access", str(context.exception))

    def test_error_with_invalid_json_raises_default_exception(self):
        """
        Test that `raise_for_error` raises the default exception when the response body is not valid JSON.
        """
        response = get_response(500)
        # Assertions
        with self.assertRaises(Amazon_AdsInternalServerError) as context:
            raise_for_error(response)
        self.assertIn("HTTP-error-code: 500", str(context.exception))

    def test_error_status_not_in_mapping_raises_default(self):
        """
        Test that `raise_for_error` raises the default exception for HTTP error status codes not present in the exception mapping.
        """
        response = get_response(418, {"message": "I'm new exception"})
        if 418 in ERROR_CODE_EXCEPTION_MAPPING:
            del ERROR_CODE_EXCEPTION_MAPPING[418]
        # Assertions
        with self.assertRaises(Amazon_AdsError) as context:
            raise_for_error(response)
        self.assertIn("I'm new exception", str(context.exception))


@patch("tap_amazon_ads.client.Client._refresh_access_token")
class TestMakeRequest(unittest.TestCase):
    """
    Unit tests for verifying the behavior of the Client class's HTTP request handling.

    This test class specifically focuses on testing the `__make_request` method of the Client class,
    ensuring that:

    - The access token is correctly set via a mocked `_refresh_access_token` method.
    - HTTP requests are made with the expected headers, parameters, and timeouts.
    - The client handles successful responses correctly.

    External calls (such as token refresh or network requests) are mocked to isolate test behavior
    and avoid making real API calls.

    The tests rely on mocking:
        - `Client._refresh_access_token` to set a fake access token
        - `requests.Session.request` to simulate API responses

    This ensures tests are fast, reliable, and not dependent on external services.
    """
    def setUp(self):
        """
        Set up common test configuration before each test case runs.
        """
        self.url = "dummy_endpoint"
        self.params = {}
        self.headers = {
            'User-Agent': 'singer',
            'Amazon-Advertising-API-ClientId': 'mocked client id',
            'Content-Type': 'application/json',
            'Amazon-Advertising-API-Scope': 'mocked profile'
            }

        self.expected_headers = self.headers.copy()
        self.expected_headers["Authorization"] = "Bearer mocked_token"

        # Mocking the Client behavior
        self.client_config = {
            "user_agent": "singer",
            "client_id": "mocked client id",
            "profiles": "mocked profile"
            }

    def fake_refresh_token(self, client_instance, *args, **kwargs):
        """
        A test helper method that simulates the behavior of the Client._refresh_access_token method.
        """
        client_instance._access_token = "mocked_token"
        client_instance._expires_at = datetime.now() + timedelta(minutes=10)

    @patch("requests.Session.request", return_value=get_response(200, {"result": []}))
    def test_successful_request(self, mocked_request, mock_refresh_token):
        """Test case for successful request."""
        # Create a client instance
        with Client(self.client_config) as client:
            # Set the side effect
            mock_refresh_token.side_effect = self.fake_refresh_token(client)
            result = client.make_request('GET', self.url, self.params, self.headers)
            # Assertions
            mocked_request.assert_called_once_with(
                "GET", self.url, headers=self.expected_headers, params=self.params, timeout=300
            )
            self.assertEqual(result, {"result": []})

    @patch("requests.Session.request", side_effect=ConnectionError)
    def test_connection_error(self, mocked_request, mock_refresh_token):
        """Test case for ConnectionError."""
        # Create a client instance
        with self.assertRaises(ConnectionError):
            with Client(self.client_config) as client:
                # Set the side effect
                mock_refresh_token.side_effect = self.fake_refresh_token(client)
                client.make_request('GET', self.url, self.params, self.headers)

        # Ensure the request was retried up to the backoff limit
        self.assertEqual(mocked_request.call_count, 5)

    @patch("requests.Session.request", side_effect=Timeout)
    def test_timeout_error(self, mocked_request, mock_refresh_token):
        """Test case for Timeout error."""
        # Create a client instance
        with self.assertRaises(Timeout):
            with Client(self.client_config) as client:
                # Set the side effect
                mock_refresh_token.side_effect = self.fake_refresh_token(client)
                client.make_request('GET', self.url, self.params, self.headers)

        # Ensure the request was retried up to the backoff limit
        self.assertEqual(mocked_request.call_count, 5)

    @patch("requests.Session.request", side_effect=ChunkedEncodingError)
    def test_chunked_encoding_error(self, mocked_request, mock_refresh_token):
        """Test case for ChunkedEncodingError."""
        # Create a client instance
        with self.assertRaises(ChunkedEncodingError):
            with Client(self.client_config) as client:
                # Set the side effect
                mock_refresh_token.side_effect = self.fake_refresh_token(client)
                client.make_request('GET', self.url, self.params, self.headers)

        # Ensure the request was retried up to the backoff limit
        self.assertEqual(mocked_request.call_count, 5)

    @patch("requests.Session.request")
    def test_rate_limit_error(self, mocked_request, mock_refresh_token):
        """Test case for 429 Rate Limit error."""
        # Simulate 5 retries for 429 error
        mocked_request.side_effect = [get_response(429, json={}, headers={"Retry-After": "3"}, raise_error=True)] * 5

        with self.assertRaises(Amazon_AdsRateLimitError):
            with Client(self.client_config) as client:
                # Set the side effect
                mock_refresh_token.side_effect = self.fake_refresh_token(client)
                client.make_request('GET', self.url, self.params, self.headers)

        # Ensure the request was retried up to the backoff limit
        self.assertEqual(mocked_request.call_count, 5)

    @patch("requests.Session.request")
    def test_authorization_error(self, mocked_request, mock_refresh_token):
        """Test case for 401 Unauthorized error."""
        mocked_request.side_effect = [
            get_response(401, {}, raise_error=True),
            get_response(401, {}, raise_error=True),
        ]
        with self.assertRaises(Amazon_AdsUnauthorizedError) as e:
            with Client(self.client_config) as client:
                # Set the side effect
                mock_refresh_token.side_effect = self.fake_refresh_token(client)
                client.make_request('GET', self.url, self.params, self.headers)

        self.assertEqual(mocked_request.call_count, 1)
        self.assertEqual(
            str(e.exception),
            "HTTP-error-code: 401, Error: The access token provided is expired, revoked, malformed or invalid for other reasons.",
        )


class TestClient(unittest.TestCase):
    """
    Unit tests for the Client class in the tap_amazon_ads module.
    """
    @patch("tap_amazon_ads.client.Client._refresh_access_token")
    @patch("tap_amazon_ads.client.datetime")
    def test_get_access_token_expired(self, mock_datetime, mock_refresh_token):
        """Test case for expired access token."""
        # Mocking the datetime to control the current time
        mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 0, 0)
        # Mocking the Client behavior
        client_config = {
            "user_agent": "singer",
            "client_id": "mocked client id",
            "profiles": "mocked profile"
            }
        client = Client(client_config)
        client._expires_at = datetime(2025, 1, 1, 11, 0, 0)
        client.get_access_token()
        client._refresh_access_token.assert_called_once()

