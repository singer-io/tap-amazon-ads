from typing import Any, Dict, Mapping, Optional, Tuple
from datetime import datetime, timedelta

import backoff
import requests
from requests import session
from requests.exceptions import Timeout, ConnectionError, ChunkedEncodingError
from singer import get_logger, metrics

from tap_amazon_ads.exceptions import ERROR_CODE_EXCEPTION_MAPPING, Amazon_AdsError, Amazon_AdsBackoffError

LOGGER = get_logger()
REQUEST_TIMEOUT = 300
REFRESH_URL = "https://api.amazon.com/auth/o2/token"

def raise_for_error(response: requests.Response) -> None:
    """Raises the associated response exception. Takes in a response object,
    checks the status code, and throws the associated exception based on the
    status code.

    :param resp: requests.Response object
    """
    try:
        response_json = response.json()
    except Exception:
        response_json = {}
    if response.status_code not in [200, 201, 204]:
        if response_json.get("error"):
            message = "HTTP-error-code: {}, Error: {}".format(response.status_code, response_json.get("error"))
        else:
            message = "HTTP-error-code: {}, Error: {}".format(
                response.status_code,
                response_json.get("message", ERROR_CODE_EXCEPTION_MAPPING.get(
                    response.status_code, {}).get("message", "Unknown Error")))
        exc = ERROR_CODE_EXCEPTION_MAPPING.get(
            response.status_code, {}).get("raise_exception", Amazon_AdsError)
        raise exc(message, response) from None

class Client:
    """
    A Wrapper class.
    ~~~
    Performs:
     - Authentication
     - Response parsing
     - HTTP Error handling and retry
    """

    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = config
        self._session = session()
        self.base_url = "https://advertising-api.amazon.com"
        self._access_token = None
        self._expires_at = None

        config_request_timeout = config.get("request_timeout")
        self.request_timeout = float(config_request_timeout) if config_request_timeout else REQUEST_TIMEOUT

    def __enter__(self):
        self._refresh_access_token()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._session.close()

    def _refresh_access_token(self) -> None:
        """Refreshes the access token."""
        LOGGER.info("Refreshing Access Token")
        resp_json = self.post(
            endpoint=REFRESH_URL,
            headers={
                "User-Agent": self.config["user_agent"],
                "content-type": "application/x-www-form-urlencoded;charset=UTF-8"
            },
            body={
                "refresh_token": self.config["refresh_token"],
                "client_id": self.config["client_id"],
                "client_secret": self.config["client_secret"],
                "grant_type": "refresh_token"
            },
            is_auth_req=False
        )
        self._access_token = resp_json["access_token"]
        expires_in_seconds = resp_json.get("expires_in", 1 * 60 * 60)
        self._expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)
        LOGGER.info("Got refreshed access token")

    def get_access_token(self) -> str:
        """Return access token if available or generate one."""
        if self._access_token and self._expires_at > datetime.now():
            return self._access_token

        self._refresh_access_token()
        return self._access_token

    @property
    def headers(self) -> Dict[str, str]:
        data = {
            'User-Agent': self.config["user_agent"],
            'Amazon-Advertising-API-ClientId': self.config["client_id"],
            "Authorization": f"Bearer {self.get_access_token()}",
            'Content-Type': 'application/json'
        }
        if profile_id := self.config["profiles"]:
            data['Amazon-Advertising-API-Scope'] = profile_id
        return data

    def authenticate(self, headers: Dict, params: Dict) -> Tuple[Dict, Dict]:
        """Authenticates the request with the token"""
        if headers is False:
            base_header = self.headers.copy()
            base_header.pop("Content-Type")
            headers = base_header
        elif headers is not None:
            base_header = self.headers.copy()
            base_header.update(headers)
            headers = base_header
        return headers, params

    def get(self, endpoint: str, params: Dict = {}, headers: Dict = {}, path: str = None, is_auth_req: bool = True) -> Any:
        """Calls the make_request method with a prefixed method type `GET`"""
        endpoint = endpoint or f"{self.base_url}/{path}"
        if is_auth_req:
            headers, params = self.authenticate(headers, params)
        return self.__make_request("GET", endpoint, headers=headers, params=params, timeout=self.request_timeout)

    def post(self, endpoint: str, params: Dict = {}, headers: Dict = {}, body: Dict = {}, path: str = None, is_auth_req: bool = True) -> Any:
        """Calls the make_request method with a prefixed method type `POST`"""
        endpoint = endpoint or f"{self.base_url}/{path}"
        if is_auth_req:
            headers, params = self.authenticate(headers, params)
        return self.__make_request("POST", endpoint, headers=headers, params=params, data=body, timeout=self.request_timeout)


    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(
            ConnectionResetError,
            ConnectionError,
            ChunkedEncodingError,
            Timeout,
            Amazon_AdsBackoffError
        ),
        max_tries=5,
        factor=2,
    )
    def __make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Mapping[Any, Any]]:
        """
        Performs HTTP Operations
        Args:
            method (str): represents the state file for the tap.
            endpoint (str): url of the resource that needs to be fetched
            params (dict): A mapping for url params eg: ?name=Avery&age=3
            headers (dict): A mapping for the headers that need to be sent
            body (dict): only applicable to post request, body of the request

        Returns:
            Dict,List,None: Returns a `Json Parsed` HTTP Response or None if exception
        """
        with metrics.http_request_timer(endpoint) as timer:
            response = self._session.request(method, endpoint, **kwargs)
            raise_for_error(response)

        return response.json()
