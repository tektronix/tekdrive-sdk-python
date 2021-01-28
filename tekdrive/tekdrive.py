"""Provide the TekDrive client"""
from logging import getLogger
from typing import TYPE_CHECKING, IO, Any, Dict, Optional, Type, Union

if TYPE_CHECKING:  # pragma: no cover
    from .routing import Route

from .core import (
    AccessKeyAuthorizer,
    ResponseException,
    Requestor,
    session,
)

from . import models
from .settings import TIMEOUT
from .exceptions import (
    ClientException,
    TekDriveAPIException,
)
from .models.parser import Parser
from .utils.casing import to_snake_case


logger = getLogger("tekdrive")


class TekDrive:

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

    def _request(
        self,
        method,
        path,
        params: Optional[Union[str, Dict[str, Union[str, int]]]] = None,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        headers: Optional[Dict[str, Union[str, Any]]] = None,
        files: Optional[Dict[str, IO]] = None,
        json=None,
    ):
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

    def request(
        self,
        route: "Route",
        params: Optional[Union[str, Dict[str, Union[str, int]]]] = None,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        headers: Optional[Dict[str, Union[str, Any]]] = None,
        files: Optional[Dict[str, IO]] = None,
        json=None,
        objectify: bool = True,
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
        if objectify:
            return self._parser.parse(
                self._request(
                    method=route.method,
                    path=route.path,
                    data=data,
                    files=files,
                    json=json,
                    params=params,
                    headers=headers,
                )
            )
        else:
            return self._request(
                method=route.method,
                path=route.path,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
            )

    # def file(
    #     self,
    #     id: Optional[str] = None,
    # ):
    #     """Return a lazy instance of :class:`~.File` for ``id``.

    #     :param id: The file id.
    #     """
    #     return models.File(self, id=id)
