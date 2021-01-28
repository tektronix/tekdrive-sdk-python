"""Provide the TekDrive client"""
import re
import time
from logging import getLogger
from typing import IO, Any, Dict, Optional, Type, Union

from .core import (
    AccessKeyAuthorizer,
    ResponseException,
    Requestor,
    session,
)

from . import models
from .settings import TIMEOUT, RATELIMIT_SECONDS
from .exceptions import (
    ClientException,
    TekDriveAPIException,
)
from .models.parser import Parser
from .utils.casing import to_snake_case


logger = getLogger("tekdrive")


class TekDrive:

    _ratelimit_regex = re.compile(r"([0-9]{1,2}) (seconds?|minutes?)")

    def __enter__(self):
        """Handle the context manager open."""
        return self

    def __exit__(self, *_args):
        """Handle the context manager close."""

    def __init__(
        self,
        access_key: str,
        requestor_class: Optional[Type[Requestor]] = None,
        requestor_kwargs: Dict[str, Any] = None,
        **config_settings: str,
    ):
        """Initialize a TekDrive instance.

        :param access_key: Previously generated TekDrive access key.
        :param requestor_class: A class that will be used to create a requestor. If not
            set, use ``tekdrive.core.Requestor`` (default: None).
        :param requestor_kwargs: Dictionary with additional keyword arguments used to
            initialize the requestor (default: None).
        """
        self._core = self._authorized_core = self._read_only_core = None
        self._parser = Parser(self, self._create_model_map())
        self._prepare_core(access_key, requestor_class, requestor_kwargs)

        self.file = models.FileHelper(self, None)

    def _create_model_map(self):
        model_map = {
            "File": models.File,
            "Member": models.Member,
            "MembersList": models.MembersList,
        }
        return model_map

    def _prepare_core(
        self, access_key: str, requestor_class=None, requestor_kwargs=None
    ):
        requestor_class = requestor_class or Requestor
        requestor_kwargs = requestor_kwargs or {}

        requestor = requestor_class(
            **requestor_kwargs,
        )

        authorizer = AccessKeyAuthorizer(access_key, requestor=requestor)

        self._core = self._authorized_core = session(authorizer)

    def get(
        self,
        path: str,
        params: Optional[Union[str, Dict[str, Union[str, int]]]] = None,
    ):
        """Return parsed objects returned from a GET request to ``path``.

        :param path: The path to fetch.
        :param params: The query parameters to add to the request (default: None).

        """
        return self._objectify_request(method="GET", params=params, path=path)

    def _objectify_request(
        self,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        files: Optional[Dict[str, IO]] = None,
        json=None,
        method: str = "",
        params: Optional[Union[str, Dict[str, str]]] = None,
        path: str = "",
    ) -> Any:
        """Run a request through the ``Objector``.

        :param data: Dictionary, bytes, or file-like object to send in the body of the
            request (default: None).
        :param files: Dictionary, filename to file (like) object mapping (default:
            None).
        :param json: JSON-serializable object to send in the body of the request with a
            Content-Type header of application/json (default: None). If ``json`` is
            provided, ``data`` should not be.
        :param method: The HTTP method (e.g., GET, POST, PUT, DELETE).
        :param params: The query parameters to add to the request (default: None).
        :param path: The path to fetch.

        """
        return self._parser.parse(
            self.request(
                data=data,
                files=files,
                json=json,
                method=method,
                params=params,
                path=path,
            )
        )

    def _handle_rate_limit(
        self, exception: TekDriveAPIException
    ) -> Optional[Union[int, float]]:
        if exception.error_code == "RATELIMIT":
            amount_search = self._ratelimit_regex.search(exception.message)
            if not amount_search:
                return None
            seconds = int(amount_search.group(1))
            if "minute" in amount_search.group(2):
                seconds *= 60
            if seconds <= int(RATELIMIT_SECONDS):
                sleep_seconds = seconds + min(seconds / 10, 1)
                return sleep_seconds
        return None

    def delete(
        self,
        path: str,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        json=None,
    ) -> Any:
        """Return parsed objects returned from a DELETE request to ``path``.

        :param path: The path to fetch.
        :param data: Dictionary, bytes, or file-like object to send in the body of the
            request (default: None).
        :param json: JSON-serializable object to send in the body of the request with a
            Content-Type header of application/json (default: None). If ``json`` is
            provided, ``data`` should not be.

        """
        return self._objectify_request(data=data, json=json, method="DELETE", path=path)

    def patch(
        self,
        path: str,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        json=None,
    ) -> Any:
        """Return parsed objects returned from a PATCH request to ``path``.

        :param path: The path to fetch.
        :param data: Dictionary, bytes, or file-like object to send in the body of the
            request (default: None).
        :param json: JSON-serializable object to send in the body of the request with a
            Content-Type header of application/json (default: None). If ``json`` is
            provided, ``data`` should not be.

        """
        return self._objectify_request(data=data, method="PATCH", path=path, json=json)

    def post(
        self,
        path: str,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        files: Optional[Dict[str, IO]] = None,
        params: Optional[Union[str, Dict[str, str]]] = None,
        json=None,
    ) -> Any:
        """Return parsed objects returned from a POST request to ``path``.

        :param path: The path to fetch.
        :param data: Dictionary, bytes, or file-like object to send in the body of the
            request (default: None).
        :param files: Dictionary, filename to file (like) object mapping (default:
            None).
        :param params: The query parameters to add to the request (default: None).
        :param json: JSON-serializable object to send in the body of the request with a
            Content-Type header of application/json (default: None). If ``json`` is
            provided, ``data`` should not be.

        """
        if json is None:
            data = data or {}
        try:
            return self._objectify_request(
                data=data,
                files=files,
                json=json,
                method="POST",
                params=params,
                path=path,
            )
        except TekDriveAPIException as exception:
            seconds = self._handle_rate_limit(exception=exception)
            if seconds is not None:
                logger.debug(f"Rate limit hit, sleeping for {seconds:.2f} seconds")
                time.sleep(seconds)
                return self._objectify_request(
                    data=data,
                    files=files,
                    method="POST",
                    params=params,
                    path=path,
                )
            raise

    def put(
        self,
        path: str,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        json=None,
    ):
        """Return parsed objects returned from a PUT request to ``path``.

        :param path: The path to fetch.
        :param data: Dictionary, bytes, or file-like object to send in the body of the
            request (default: None).
        :param json: JSON-serializable object to send in the body of the request with a
            Content-Type header of application/json (default: None). If ``json`` is
            provided, ``data`` should not be.

        """
        return self._objectify_request(data=data, json=json, method="PUT", path=path)

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Union[str, Dict[str, Union[str, int]]]] = None,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        headers: Optional[Dict[str, Union[str, Any]]] = None,
        files: Optional[Dict[str, IO]] = None,
        json=None,
    ) -> Any:
        """Return the parsed JSON data returned from a request to URL.

        :param method: The HTTP method (e.g., GET, POST, PUT, DELETE).
        :param path: The path to fetch.
        :param params: The query parameters to add to the request (default: None).
        :param data: Dictionary, bytes, or file-like object to send in the body of the
            request (default: None).
        :param files: Dictionary, filename to file (like) object mapping (default:
            None).
        :param json: JSON-serializable object to send in the body of the request with a
            Content-Type header of application/json (default: None). If ``json`` is
            provided, ``data`` should not be.

        """
        if data and json:
            raise ClientException("Only supply one of: `json`, `data`.")
        try:
            return self._core.request(
                method,
                path,
                data=data,
                files=files,
                params=params,
                headers=headers,
                timeout=TIMEOUT,
                json=json,
            )
        except ResponseException as exception:
            try:
                error_info = exception.response.json()
            except ValueError:
                raise Exception(
                    "Unexpected ResponseException"
                ) from exception
            
            # expected error format from API
            raise TekDriveAPIException(to_snake_case(error_info)) from exception

    # def file(
    #     self,
    #     id: Optional[str] = None,
    # ):
    #     """Return a lazy instance of :class:`~.File` for ``id``.

    #     :param id: The file id.
    #     """
    #     return models.File(self, id=id)
