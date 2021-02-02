"""Provides the Folder class."""
from typing import TYPE_CHECKING, Any, Dict, Optional, List, Union

from ...routing import Route, ENDPOINTS
from ...utils.casing import to_snake_case
from .base import DriveBase
from .member import Member

if TYPE_CHECKING:  # pragma: no cover
    from .. import TekDrive


class Folder(DriveBase):
    STR_FIELD = "id"

    def __init__(
        self,
        tekdrive: "TekDrive",
        id: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        fetched = False
        if id:
            self.id = id
        else:
            fetched = True

        super().__init__(tekdrive, _data=_data, _fetched=fetched)

    def __setattr__(
        self,
        attribute: str,
        value: Union[str, int, "Member"],
    ):
        """Parse owner and creator into members."""
        if attribute == "owner" or attribute == "creator":
            value = Member.from_data(self._tekdrive, value)
        super().__setattr__(attribute, value)

    def _fetch_data(self):
        route = Route('GET', ENDPOINTS["folder_details"], folder_id=self.id)
        return self._tekdrive.request(route, objectify=False)

    def _fetch(self):
        data = self._fetch_data()
        other = type(self)(self._tekdrive, _data=to_snake_case(data))
        self.__dict__.update(other.__dict__)
        self._fetched = True

    def _update_details(self, data):
        route = Route("PUT", ENDPOINTS["folder_details"], folder_id=self.id)
        return self._tekdrive.request(route, json=data)

    @staticmethod
    def _create(
        _tekdrive,
        name: str = None,
        parent_folder_id: str = None,
    ) -> "Folder":
        data = dict(name=name, parentFolderId=parent_folder_id)
        route = Route("POST", ENDPOINTS["folder_create"])
        new_folder = _tekdrive.request(route, json=data)
        return new_folder

    def members(self) -> List[Member]:
        """Return a list of folder members"""
        route = Route("GET", ENDPOINTS["folder_members"], folder_id=self.id)
        return self._tekdrive.request(route)

    def move(self, parent_folder_id: str) -> None:
        data = dict(parentFolderId=parent_folder_id)
        self._update_details(data)
        self.parent_folder_id = parent_folder_id

    def save(self) -> None:
        data = dict(name=self.name)
        self._update_details(data)

    # TODO: folder should expose an upload() method that uploads a file into the folder
