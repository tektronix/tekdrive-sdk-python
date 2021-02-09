"""Provides the Search class."""
from typing import TYPE_CHECKING, Iterator, List, Optional, Union

from ..routing import Route, ENDPOINTS
from .base import TekDriveBase
from .paginator import PaginatedListGenerator
from . import File, Folder
from ..exceptions import ClientException
from ..utils.casing import to_camel_case

if TYPE_CHECKING:  # pragma: no cover
    from .. import TekDrive


class Search(TekDriveBase):
    def __init__(self, tekdrive: "TekDrive"):
        super().__init__(tekdrive, _data=None)

    def query(
        self,
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
    ) -> Iterator[Union[File, Folder]]:
        """
        Run search query.

        :param limit: Total limit for returned results.
        """
        if all(param is None for param in [name, file_type]):
            raise ClientException("Must supply `name`, `file_type`, or `upload_state`.")

        route = Route("GET", ENDPOINTS["search"])

        search_types = []
        if include_files is True:
            search_types.append("FILE")
        if include_folders is True:
            search_types.append("FOLDER")

        params = to_camel_case(dict(
            folder_id=folder_id,
            name=name,
            silo=silo,
            depth=depth,
            file_type=file_type,
            type=search_types,
            upload_state=upload_state,
            order_by=order_by
        ))
        return PaginatedListGenerator(self._tekdrive, route, limit=limit, params=params)
