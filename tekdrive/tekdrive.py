"""Provide the TekDrive client"""
from logging import getLogger
from typing import TYPE_CHECKING, IO, Any, Dict, Optional, Type, Union

if TYPE_CHECKING:
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
    def __init__(
        self,
        access_key: str,
        requestor_class: Optional[Type[Requestor]] = None,
        requestor_kwargs: Dict[str, Any] = None,
        **config_settings: str,
    ):
        """
        Initialize a TekDrive instance.

        Args:
            access_key: Previously generated TekDrive access key.
            requestor_class: A class that will be used to create a requestor. If not
                set, use ``tekdrive.core.Requestor``.
            requestor_kwargs: Dictionary with additional keyword arguments used to
                initialize the requestor.
        """
        if not access_key:
            raise ClientException("Missing required attribute 'access_key'.")

        self._core = None
        self._parser = Parser(self, self._create_model_map())
        self._prepare_core(access_key, requestor_class, requestor_kwargs)

        self.file = models.FileHelper(self, None)
        self.folder = models.FolderHelper(self, None)

        self.search = models.Search(self)
        self.user = models.User(self)

    def __enter__(self):
        """Context manager enter"""
        return self

    def __exit__(self, *_args):
        """Context manager exit"""
        pass

    def _create_model_map(self):
        model_map = {
            "File": models.File,
            "Folder": models.Folder,
            "Member": models.Member,
            "MembersList": models.MembersList,
            "PaginatedList": models.PaginatedList,
            "DriveUser": models.DriveUser,
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

        self._core = session(authorizer)

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
            raise ClientException("Only supply one of: 'json', 'data'.")
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
                raise Exception("Unexpected ResponseException") from exception

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
        should_parse: bool = True,
    ) -> Any:
        """
        Return the parsed JSON data returned from a request to URL.

        Args:
            method: The HTTP method (e.g., GET, POST, PUT, DELETE).
            path: The path to fetch.
            params: The query parameters to add to the request.
            data: Dictionary, bytes, or file-like object to send in the body of the
                request.
            files: Dictionary, filename to file (like) object mapping
            json: JSON-serializable object to send in the body of the request with a
                Content-Type header of application/json. If ``json`` is provided,
                ``data`` should not be.

        """
        if should_parse:
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
