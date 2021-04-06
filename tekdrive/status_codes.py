from requests.exceptions import (
    ChunkedEncodingError,
    ConnectionError,
    Timeout,  # both ConnectTimeout and ReadTimeout errors
)
from requests.status_codes import codes as http_codes

from .exceptions import (
    BadRequest,
    Unauthorized,
    Forbidden,
    NotFound,
    Conflict,
    Gone,
    Unprocessable,
    ServerError,
)

NO_CONTENT = http_codes.NO_CONTENT
SUCCESS_STATUS_CODES = (http_codes.CREATED, http_codes.OK)
RETRY_STATUS_CODES = (
    http_codes.BAD_GATEWAY,
    http_codes.GATEWAY_TIMEOUT,
    http_codes.INTERNAL_SERVER_ERROR,
    http_codes.SERVICE_UNAVAILABLE,
    520,  # Web server is returning an unknown error a.k.a "catch-all"
    522,  # Connection timed out
)
RETRY_EXCEPTIONS = (ChunkedEncodingError, ConnectionError, Timeout)

STATUS_TO_EXCEPTION_MAPPING = {
    http_codes.BAD_GATEWAY: ServerError,
    http_codes.BAD_REQUEST: BadRequest,
    http_codes.CONFLICT: Conflict,
    http_codes.FORBIDDEN: Forbidden,
    http_codes.NOT_FOUND: NotFound,
    http_codes.GONE: Gone,
    http_codes.GATEWAY_TIMEOUT: ServerError,
    http_codes.INTERNAL_SERVER_ERROR: ServerError,
    http_codes.SERVICE_UNAVAILABLE: ServerError,
    http_codes.UNAUTHORIZED: Unauthorized,
    http_codes.UNPROCESSABLE_ENTITY: Unprocessable,
}
EXCEPTION_STATUS_CODES = [code for code in STATUS_TO_EXCEPTION_MAPPING.keys()]
