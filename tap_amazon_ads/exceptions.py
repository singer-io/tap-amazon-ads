class Amazon_AdsError(Exception):
    """class representing Generic Http error."""

    def __init__(self, message=None, response=None):
        try:
            super().__init__(message)
            self.message = message
            self.response = response
            self.amzn_error_details = response.get('details')
            self.amzn_code = response.get('code')
        except (IndexError, AttributeError):
            pass

    def get_amzn_code(self):
        return self.amzn_code

    def get_amzn_error_details(self):
        return self.amzn_error_details


class Amazon_AdsBackoffError(Amazon_AdsError):
    """class representing backoff error handling."""
    pass

class Amazon_AdsBadRequestError(Amazon_AdsError):
    """class representing 400 status code."""
    pass

class Amazon_AdsUnauthorizedError(Amazon_AdsError):
    """class representing 401 status code."""
    pass

class Amazon_AdsForbiddenError(Amazon_AdsError):
    """class representing 403 status code."""
    pass

class Amazon_AdsNotFoundError(Amazon_AdsError):
    """class representing 404 status code."""
    pass

class Amazon_AdsConflictError(Amazon_AdsError):
    """class representing 406 status code."""
    pass

class Amazon_AdsUnprocessableEntityError(Amazon_AdsBackoffError):
    """class representing 409 status code."""
    pass

class Amazon_AdsRateLimitError(Amazon_AdsBackoffError):
    """class representing 429 status code."""
    pass

class Amazon_AdsInternalServerError(Amazon_AdsBackoffError):
    """class representing 500 status code."""
    pass

class Amazon_AdsNotImplementedError(Amazon_AdsBackoffError):
    """class representing 501 status code."""
    pass

class Amazon_AdsBadGatewayError(Amazon_AdsBackoffError):
    """class representing 502 status code."""
    pass

class Amazon_AdsServiceUnavailableError(Amazon_AdsBackoffError):
    """class representing 503 status code."""
    pass

class Amazon_AdsGatewayTimeout(Amazon_AdsBackoffError):
    """class representing 504 status code."""
    pass

ERROR_CODE_EXCEPTION_MAPPING = {
    400: {
        "raise_exception": Amazon_AdsBadRequestError,
        "message": "A validation exception has occurred."
    },
    401: {
        "raise_exception": Amazon_AdsUnauthorizedError,
        "message": "The access token provided is expired, revoked, malformed or invalid for other reasons."
    },
    403: {
        "raise_exception": Amazon_AdsForbiddenError,
        "message": "You are missing the following required scopes: read"
    },
    404: {
        "raise_exception": Amazon_AdsNotFoundError,
        "message": "The resource you have specified cannot be found."
    },
    409: {
        "raise_exception": Amazon_AdsConflictError,
        "message": "The API request cannot be completed because the requested operation would conflict with an existing item."
    },
    422: {
        "raise_exception": Amazon_AdsUnprocessableEntityError,
        "message": "The request content itself is not processable by the server."
    },
    429: {
        "raise_exception": Amazon_AdsRateLimitError,
        "message": "The API rate limit for your organisation/application pairing has been exceeded."
    },
    500: {
        "raise_exception": Amazon_AdsInternalServerError,
        "message": "The server encountered an unexpected condition which prevented" \
            " it from fulfilling the request."
    },
    501: {
        "raise_exception": Amazon_AdsNotImplementedError,
        "message": "The server does not support the functionality required to fulfill the request."
    },
    502: {
        "raise_exception": Amazon_AdsBadGatewayError,
        "message": "Server received an invalid response."
    },
    503: {
        "raise_exception": Amazon_AdsServiceUnavailableError,
        "message": "API service is currently unavailable."
    },
    504: {
        "raise_exception": Amazon_AdsGatewayTimeout,
        "message": "API request timed out after waiting for a response."
    }
}

