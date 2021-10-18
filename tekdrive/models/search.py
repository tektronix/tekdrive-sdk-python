"""Provides the Search class."""
from typing import TYPE_CHECKING, Iterator, List, Optional, Union

from ..routing import Route, ENDPOINTS
from .base import TekDriveBase
from .paginator import PaginatedListGenerator
from . import File, Folder
from ..exceptions import ClientException
from ..utils.casing import to_camel_case

if TYPE_CHECKING:
    from .. import TekDrive


class Search(TekDriveBase):
    """
    Provides various methods to help with searching for TekDrive files and folders.
    """

    def __init__(self, tekdrive: "TekDrive"):
        super().__init__(tekdrive=tekdrive, _data=None)

    def files(
        self,
        *,
        name: Optional[str] = None,
        limit: Optional[int] = 100,
        folder_id: [str] = None,
        silo: Optional[str] = None,
        depth: Optional[int] = 1,
        file_type: Optional[List[str]] = None,
        upload_state: Optional[List[str]] = None,
        order_by: Optional[List[str]] = None,
        include_trashed: bool = False,
    ) -> Iterator[File]:
        """
        Convenience method for files search.

        Args:
            limit: Total limit for returned results.
            name: File name to match on. Case insensitive.
            folder_id: Unique ID of folder to perform search within.
            silo: Name of the silo to perform the search within. Values: ``"SHARES"`` or ``"PERSONAL"``.
            depth: How many levels deep to perform search when specifying a ``folder_id`` or ``silo``.
            file_type: Limit results to files matching the given file type(s).
            upload_state: Limit results to files in the given upload state(s).

        Examples:
            Get up to 50 WFM files::

                results = td.search.files(file_type="WFM", limit=50)

        Returns:
            Iterator [ :ref:`file` ]

        """
        return self.query(
            limit=limit,
            include_files=True,
            include_folders=False,
            folder_id=folder_id,
            silo=silo,
            depth=depth,
            file_type=file_type,
            upload_state=upload_state,
            name=name,
            order_by=order_by,
            include_trashed=include_trashed,
        )

    def folders(
        self,
        *,
        name: Optional[str] = None,
        limit: Optional[int] = 100,
        folder_id: [str] = None,
        silo: Optional[str] = None,
        depth: Optional[int] = 1,
        order_by: Optional[List[str]] = None,
        include_trashed: bool = False,
    ) -> Iterator[Folder]:
        """
        Convenience method for folders search.

        Args:
            limit: Total limit for returned results.
            silo: Name of the silo to perform the search within. Values: ``"SHARES"`` or ``"PERSONAL"``.
            name: Folder name to match on. Case insensitive.
            folder_id: Unique ID of folder to perform search within.
            depth: How many levels deep to perform search when specifying a ``folder_id`` or ``silo``.

        Examples:
            Get up to 10 folders with a name like ``"team_"``::

                results = td.search.folders(name="team_", limit=10)

        Returns:
            Iterator [ :ref:`folder` ]
        """
        return self.query(
            limit=limit,
            include_files=False,
            include_folders=True,
            folder_id=folder_id,
            silo=silo,
            depth=depth,
            name=name,
            order_by=order_by,
            include_trashed=include_trashed,
        )

    def query(
        self,
        *,
        name: Optional[str] = None,
        limit: Optional[int] = 100,
        folder_id: [str] = None,
        silo: Optional[str] = None,
        depth: Optional[int] = 1,
        file_type: Optional[List[str]] = None,
        include_files: bool = True,
        include_folders: bool = True,
        upload_state: Optional[List[str]] = None,
        order_by: Optional[List[str]] = None,
        include_trashed: bool = False,
    ) -> Iterator[Union[File, Folder]]:
        """
        Execute search for files and/or folders matching the provided criteria. A global search will
        be performed by default unless a ``folder_id`` or ``silo`` is provided.

        Args:
            limit: Total limit for returned results.
            name: File/Folder name to match on. Case insensitive.
            folder_id: Unique ID of folder to perform search within.
            depth: How many levels deep to perform search when specifying a ``folder_id`` or ``silo``.
            silo: Name of the silo to perform the search within. Values: ``"SHARES"`` or ``"PERSONAL"``.
            file_type: Limit results to files matching the given file type(s).
            include_files: Include files in the search results? Default: ``True``.
            include_folders: Include folders in the search results? Default: ``True``.
            upload_state: Limit results to files in the given upload state(s).
            include_trashed: Include files and folders in the trashcan.

        Examples:
            Get files with name like ``"project1"``::

                results = td.search.query(name="project1", include_folders=False)

        Returns:
            Iterator [ Union [ :ref:`file` , :ref:`folder` ] ]
        """
        if all(param is None for param in [name, file_type]):
            raise ClientException("Must supply `name`, `file_type`, or `upload_state`.")

        route = Route("GET", ENDPOINTS["search"])

        search_types = []
        if include_files is True:
            search_types.append("FILE")
        if include_folders is True:
            search_types.append("FOLDER")

        params = to_camel_case(
            dict(
                folder_id=folder_id,
                name=name,
                silo=silo,
                depth=depth,
                file_type=file_type,
                type=",".join(search_types),
                upload_state=upload_state,
                order_by=order_by,
                include_trashed=include_trashed,
            )
        )
        return PaginatedListGenerator(self._tekdrive, route, limit=limit, params=params)
