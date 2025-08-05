class AmazonAdsError(Exception):
    """class representing Generic Http error."""

    def __init__(self, message=None, response=None):
        super().__init__(message)
        self.message = message
        self.response = response

class AmazonAdsBackoffError(AmazonAdsError):
    """class representing backoff error handling."""
    pass

class AmazonAdsBadRequestError(AmazonAdsError):
    """class representing 400 status code."""
    pass

class AmazonAdsUnauthorizedError(AmazonAdsError):
    """class representing 401 status code."""
    pass

class AmazonAdsForbiddenError(AmazonAdsError):
    """class representing 403 status code."""
    pass

class AmazonAdsNotFoundError(AmazonAdsError):
    """class representing 404 status code."""
    pass

class AmazonAdsConflictError(AmazonAdsError):
    """class representing 406 status code."""
    pass

class AmazonAdsUnprocessableEntityError(AmazonAdsBackoffError):
    """class representing 409 status code."""
    pass

class AmazonAdsRateLimitError(AmazonAdsBackoffError):
    """class representing 429 status code."""
    def __init__(self, message=None, response=None):
        """Initialize the Amazon_AdsRateLimitError. Parses the 'Retry-After' header from the response (if present) and sets the
            `retry_after` attribute accordingly.
        """
        self.response = response

        # Retry-After header parsing
        retry_after = None
        if response and hasattr(response, 'headers'):
            raw_retry = response.headers.get('Retry-After')
            if raw_retry:
                try:
                    retry_after = int(raw_retry)
                except ValueError:
                    retry_after = None

        self.retry_after = retry_after
        base_msg = message or "Rate limit hit"
        retry_info = f"(Retry after {self.retry_after} seconds.)" \
            if self.retry_after is not None else "(Retry after unknown delay.)"
        full_message = f"{base_msg} {retry_info}"
        super().__init__(full_message, response=response)

class AmazonAdsInternalServerError(AmazonAdsBackoffError):
    """class representing 500 status code."""
    pass

class AmazonAdsNotImplementedError(AmazonAdsBackoffError):
    """class representing 501 status code."""
    pass

class AmazonAdsBadGatewayError(AmazonAdsBackoffError):
    """class representing 502 status code."""
    pass

class AmazonAdsServiceUnavailableError(AmazonAdsBackoffError):
    """class representing 503 status code."""
    pass

class AmazonAdsGatewayTimeout(AmazonAdsBackoffError):
    """class representing 504 status code."""
    pass

ERROR_CODE_EXCEPTION_MAPPING = {
    400: {
        "raise_exception": AmazonAdsBadRequestError,
        "message": "A validation exception has occurred."
    },
    401: {
        "raise_exception": AmazonAdsUnauthorizedError,
        "message": "The access token provided is expired, revoked, malformed or invalid for other reasons."
    },
    403: {
        "raise_exception": AmazonAdsForbiddenError,
        "message": "You are missing the following required scopes: read"
    },
    404: {
        "raise_exception": AmazonAdsNotFoundError,
        "message": "The resource you have specified cannot be found."
    },
    409: {
        "raise_exception": AmazonAdsConflictError,
        "message": "The API request cannot be completed because the requested operation would conflict with an existing item."
    },
    422: {
        "raise_exception": AmazonAdsUnprocessableEntityError,
        "message": "The request content itself is not processable by the server."
    },
    429: {
        "raise_exception": AmazonAdsRateLimitError,
        "message": "The API rate limit for your organisation/application pairing has been exceeded."
    },
    500: {
        "raise_exception": AmazonAdsInternalServerError,
        "message": "The server encountered an unexpected condition which prevented" \
            " it from fulfilling the request."
    },
    501: {
        "raise_exception": AmazonAdsNotImplementedError,
        "message": "The server does not support the functionality required to fulfill the request."
    },
    502: {
        "raise_exception": AmazonAdsBadGatewayError,
        "message": "Server received an invalid response."
    },
    503: {
        "raise_exception": AmazonAdsServiceUnavailableError,
        "message": "API service is currently unavailable."
    },
    504: {
        "raise_exception": AmazonAdsGatewayTimeout,
        "message": "API request timed out after waiting for a response."
    }
}

