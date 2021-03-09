"""Provide exception classes"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests import Response


class TekDriveException(Exception):
    """The base TekDrive Exception that all other exception classes extend."""


class TekDriveAPIException(TekDriveException):
    def __init__(
        self,
        data: dict,
        *,
        headers: dict = {},
    ):
        self.data = data
        self.headers = headers

    @property
    def error_code(self) -> str:
        return self.data.get("error_code")

    @property
    def message(self) -> str:
        return self.data.get("message")

    @property
    def errors(self):
        return self.data.get("errors")

    @property
    def request_id(self):
        return self.headers.get("X-Request-Id")


class TekDriveStorageException(TekDriveException):
    """Indicate exceptions that happen uploading/downloading from storage."""


class ClientException(TekDriveException):
    """Indicate exceptions that happen client side."""


class InvalidAuthorizer(TekDriveException):
    """Indicate the authorizer is invalid and the request cannot be made."""


class HTTPException(TekDriveException):
    """Indicate an error with an HTTP request."""


class RequestException(HTTPException):
    """Indicate that there was an error with the incomplete HTTP request."""

    def __init__(self, original_exception, request_args, request_kwargs):
        """
        Args:
            original_exception: The original exception that occurred.
            request_args: The arguments to the request function.
            request_kwargs: The keyword arguments to the request function.
        """
        self.original_exception = original_exception
        self.request_args = request_args
        self.request_kwargs = request_kwargs
        super(RequestException, self).__init__(
            f"Error with request {original_exception}"
        )


class ResponseException(HTTPException):
    """Indicate that there was an error with the completed HTTP request."""

    def __init__(self, response: "Response"):
        self.response = response
        super(ResponseException, self).__init__(
            f"Received {response.status_code} HTTP response"
        )


class BadRequest(ResponseException):
    """Indicate a malformed request."""


class BadJSON(ResponseException):
    """Indicate the response did not contain valid JSON."""


class Unauthorized(ResponseException):
    """Indicate invalid credentials for the target resource."""


class Forbidden(ResponseException):
    """Indicate invalid permissions to complete the requested action."""


class NotFound(ResponseException):
    """Indicate that the requested resource was not found."""


class Conflict(ResponseException):
    """Indicate a conflicting change in the target resource."""


class Unprocessable(ResponseException):
    """Indicate the request was not processable."""


class ServerError(ResponseException):
    """Indicate issues on the server end"""
