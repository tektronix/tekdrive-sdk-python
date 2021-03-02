"""Provides the User class."""
from typing import TYPE_CHECKING

from ..routing import Route, ENDPOINTS
from .base import TekDriveBase
from . import DriveUser

if TYPE_CHECKING:  # pragma: no cover
    from .. import TekDrive


class User(TekDriveBase):
    def __init__(self, tekdrive: "TekDrive"):
        super().__init__(tekdrive, _data=None)

    def me(self) -> DriveUser:
        route = Route("GET", ENDPOINTS["user"])
        return self._tekdrive.request(route)

    def usage(self):
        # TODO:
        pass
