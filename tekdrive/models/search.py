"""Provides the Search class."""
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Union

from ..routing import Route, ENDPOINTS
from .base import TekDriveBase
from .paginator import PaginatedListGenerator
from . import File, Folder

if TYPE_CHECKING:  # pragma: no cover
    from .. import TekDrive


class Search(TekDriveBase):
    def __init__(self, tekdrive: "TekDrive"):
        super().__init__(tekdrive, _data=None)

    def query(self, name=None, limit=100) -> Iterator[Union[File, Folder]]:
        route = Route("GET", ENDPOINTS["search"])
        return PaginatedListGenerator(self._tekdrive, route, limit=limit, params=dict(name=name))
