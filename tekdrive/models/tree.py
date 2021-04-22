"""Provides the Tree class."""
from typing import TYPE_CHECKING, Iterator, List, Optional, Union

from ..routing import Route, ENDPOINTS
from .base import TekDriveBase
from .paginator import PaginatedListGenerator
from . import File, Folder
from ..exceptions import ClientException
from ..utils.casing import to_camel_case

if TYPE_CHECKING:
    from .. import TekDrive


class Tree(TekDriveBase):
    """
    Provides recursive directory listing down to a certain depth.
    """

    def __init__(self, tekdrive: "TekDrive"):
        super().__init__(tekdrive=tekdrive, _data=None)

    def get(
        self,
        *,
        folder_id: [str] = None,
        limit: Optional[int] = 100,
        silo: Optional[str] = None,
        depth: Optional[int] = 1,
        folders_only: bool = False,
        include_trashed: bool = False,
    ):

        route = Route("GET", ENDPOINTS["tree"])
        params = to_camel_case(
            dict(
                folder_id=folder_id,
                silo=silo,
                depth=depth,
                folders_only=folders_only,
                # TODO: can just use `include_trashed=include_trashed` once API properly lowercases param value
                include_trashed='true' if include_trashed else 'false',
            )
        )
        # TODO: does return need to change?
        return self._tekdrive.request(route)