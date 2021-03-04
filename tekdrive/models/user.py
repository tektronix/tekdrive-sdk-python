"""Provides the User class."""
from typing import TYPE_CHECKING

from ..routing import Route, ENDPOINTS
from .base import TekDriveBase
from . import DriveUser
from .usage import Usage

if TYPE_CHECKING:
    from .. import TekDrive


class User(TekDriveBase):
    def __init__(self, tekdrive: "TekDrive"):
        super().__init__(tekdrive, _data=None)

    def me(self) -> DriveUser:
        """
        Get user details for the authenticated user.

        Examples:
            Fetch user details::

                me = td.user.me()

            Get the plan the user is on::

                plan = td.user.me().plan

        """
        route = Route("GET", ENDPOINTS["user"])
        return self._tekdrive.request(route)

    def usage(self) -> Usage:
        """
        Get TekDrive usage details for the authenticated user.

        Examples:
            Fetch usage details::

                usage_info = td.user.usage()

        """
        route = Route("GET", ENDPOINTS["usage"])
        data = self._tekdrive.request(route)
        return Usage(
            total_bytes_owned=data["total_bytes_owned"],
            files_owned_count=data["files_owned_count"],
            total_bytes_owned_in_trash=data["total_bytes_owned_in_trash"],
            files_owned_in_trash_count=data["files_owned_in_trash_count"],
            total_bytes_created=data["total_bytes_created"],
            files_created_count=data["files_created_count"],
            storage_size_limit=data["storage_size_limit"],
        )
