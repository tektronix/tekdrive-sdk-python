"""Provides the Trash class."""
from typing import TYPE_CHECKING, Iterator, List, Optional, Union

from ..routing import Route, ENDPOINTS
from .base import TekDriveBase
from .paginator import PaginatedListGenerator
from . import File, Folder
from ..exceptions import ClientException
from ..utils.casing import to_camel_case

if TYPE_CHECKING:
    from .. import TekDrive


class Trashcan(TekDriveBase):
    """
    Provides various methods to help with managing items in the trashcan.
    """

    def __init__(self, tekdrive: "TekDrive"):
        super().__init__(tekdrive=tekdrive, _data=None)

    def empty(
        self,
    ) -> None:
        """
        Empty all items currently in the trash.

        Examples:
            Empty the trashcan::

                td.trash.empty()
        """
        route = Route("DELETE", ENDPOINTS["trash"])
        self._tekdrive.request(route)

    def get(
        self,
        *,
        order_by: List[str] = ["-trashedAt"],
        limit: Optional[int] = 100,
    ):
        """
        Get items currently in the trash.

        Examples:
            Get the first 10 items in the trashcan::

                td.trash.get(limit=10)
        """
        route = Route("GET", ENDPOINTS["trash"])
        params = to_camel_case(
            dict(
                order_by=order_by,
            )
        )
        return PaginatedListGenerator(self._tekdrive, route, limit=limit, params=params)
