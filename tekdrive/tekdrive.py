"""Provide the TekDrive client"""
import logging
from typing import TYPE_CHECKING, IO, Any, Dict, Optional, Union

from .authorizer import AccessKeyAuthorizer
from .session import create_session

from . import models
from .settings import TIMEOUT, BASE_URL
from .exceptions import (
    ClientException,
    ResponseException,
    TekDriveAPIException,
)
from .models.parser import Parser
from .utils.casing import to_snake_case

if TYPE_CHECKING:
    from .routing import Route

logging.getLogger("tekdrive").addHandler(logging.NullHandler())


class TekDrive:
    def __init__(
        self,
        access_key: str,
        base_url: str = BASE_URL,
        debug_mode: bool = False
    ):
        """
        Initialize a TekDrive instance.

        Args:
            access_key: Previously generated TekDrive access key.
            base_url: Base url for the TekDrive API.
            debug_mode: Should enable debug logging?
        """
        if not access_key:
            raise ClientException("Missing required attribute 'access_key'.")

        if debug_mode:
            logging.basicConfig(level=logging.DEBUG)

        # create authorizer and session
        self._authorizer = AccessKeyAuthorizer(access_key=access_key)
        self._session = create_session(authorizer=self._authorizer, base_url=base_url)

        # prepare parser
        self._parser = Parser(self, self._create_model_map())

        # models and helpers
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

    def _request(
        self,
        route: "Route",
        params: Optional[Union[str, Dict[str, Union[str, int]]]] = None,
        data: Optional[Union[Dict[str, Union[str, Any]], bytes, IO, str]] = None,
        headers: Optional[Dict[str, Union[str, Any]]] = None,
        files: Optional[Dict[str, IO]] = None,
        json=None,
    ):
        if data and json:
            raise ClientException("Only supply one of: 'json', 'data'.")
        try:
            return self._session.request(
                route=route,
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

            api_error = self._parser.parse_error(error_info, headers=exception.response.headers)
            if api_error:
                # expected error format from API with known error code
                raise api_error from exception
            else:
                # raise generic api exception
                raise TekDriveAPIException(to_snake_case(error_info), headers=exception.response.headers) from exception

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
        Return JSON data returned from a request using the provided route.

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
            should_parse: Should the response be parsed into a TekDrive model?
        """
        data = self._request(
            route=route,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
        )
        if should_parse:
            return self._parser.parse(data)
        else:
            return data
