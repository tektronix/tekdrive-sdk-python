"""Provides the File class."""
import os
import requests
from typing import TYPE_CHECKING, Any, Dict, IO, Optional, List, Union

from ...routing import Route, ENDPOINTS
from ...exceptions import TekDriveStorageException
from ...utils.casing import to_snake_case
from .base import DriveBase
from .member import Member

if TYPE_CHECKING:  # pragma: no cover
    from .. import TekDrive


class File(DriveBase):
    STR_FIELD = "id"

    def __init__(
        self,
        tekdrive: "TekDrive",
        id: Optional[str] = None,
        file_path: Optional[str] = None,
        name: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        fetched = False
        if id:
            self.id = id
        else:
            fetched = True

        self._upload_url = None

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
        route = Route('GET', '/file/{file_id}', file_id=self.id)
        return self._tekdrive.request(route, objectify=False)

    def _fetch(self):
        data = self._fetch_data()
        other = type(self)(self._tekdrive, _data=to_snake_case(data))
        self.__dict__.update(other.__dict__)
        self._fetched = True

    def _fetch_upload_url(self):
        route = Route("GET", ENDPOINTS["file_members"], file_id=self.id)
        upload_details = self._tekdrive.request(route)
        return upload_details["upload_url"]

    def _upload_to_storage(self, upload_url: str, file: IO):
        try:
            r = requests.put(
                upload_url,
                data=file,
                headers={
                    "Content-Type": "application/octet-stream",
                },
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as exception:
            raise TekDriveStorageException("Upload failed") from exception

    @staticmethod
    def _create(
        _tekdrive,
        file_path: str = None,
        name: str = None,
    ) -> "File":
        if file_path and name is None:
            name = os.path.basename(file_path)

        data = dict(name=name)
        route = Route("POST", ENDPOINTS["file_create"])
        new_file = _tekdrive.request(route, json=data)

        if file_path:
            new_file.upload(file_path)

        return new_file

    def members(self) -> List[Member]:
        """Return a list of file members"""
        route = Route("GET", ENDPOINTS["file_members"], file_id=self.id)
        return self._tekdrive.request(route)

    def upload(self, file_path: str) -> None:
        # TODO: multipart upload support
        if self._upload_url is None:
            self._upload_url = self._fetch_upload_url()

        # do single upload
        with open(file_path, "rb") as f:
            self._upload_to_storage(self._upload_url, f)
