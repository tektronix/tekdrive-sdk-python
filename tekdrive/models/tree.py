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
    Provides directory listing.
    """

    def __init__(self, tekdrive: "TekDrive"):
        super().__init__(tekdrive=tekdrive, _data=None)

    def get(
        self,
        *,
        folder_id: [str] = None,
        silo: Optional[str] = None,
        depth: Optional[int] = 1,
        folders_only: bool = False,
        include_trashed: bool = False,
    ) -> Folder:
        """
        Get the tree representation from a starting folder.

        Args:
            folder_id: Unique ID of starting folder to start the tree from.
            depth: How many nested levels to return.
            silo: Get tree for the provided silo. Values: ``"SHARES"`` or ``"PERSONAL"``.
            folders_only: Only include folders in the tree results? Default: ``False``.
            include_trashed: Include files and folders that are in the trashcan.

        Examples:
            Get tree from starting folder by id::

                tree = td.tree.get(folder_id="3b525331-9da7-4e8d-b045-4acdba8d9dc7")

            Get tree for the ``SHARES`` silo, excluding files::

                tree = td.tree.get(silo="SHARES", folders_only=True)
        """

        route = Route("GET", ENDPOINTS["tree"])
        params = to_camel_case(
            dict(
                folder_id=folder_id,
                silo=silo,
                depth=depth,
                folders_only=folders_only,
                include_trashed=include_trashed,
            )
        )
        return self._tekdrive.request(route, params=params)
