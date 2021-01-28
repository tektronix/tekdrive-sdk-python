"""Provides the User class."""
import requests
from typing import TYPE_CHECKING, Any, Dict, IO, Optional, List, Union

from ...exceptions import TekDriveStorageException
from ...endpoints import ENDPOINTS
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

    def _fetch_info(self):
        return "file_details", {"file_id": self.id}, {}

    def _fetch_data(self):
        name, fields, params = self._fetch_info()
        path = ENDPOINTS[name].format(**fields)
        return self._tekdrive.request("GET", path, params)

    def _fetch(self):
        data = self._fetch_data()
        data = to_snake_case(data)
        other = type(self)(self._tekdrive, _data=data)
        self.__dict__.update(other.__dict__)
        self._fetched = True

    def _upload_to_storage(self, upload_url, file):
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
        name=None,
    ) -> "File":
        data = dict(name=name)
        new_file = _tekdrive.post(ENDPOINTS["file_create"], json=data)
        return new_file

    def members(self) -> List[Member]:
        """Return a list of file members"""
        return self._tekdrive.get(ENDPOINTS["file_members"].format(file_id=self.id))

    def upload(self, file: IO) -> None:
        # TODO: multipart upload support
        if self._upload_url is None:
            upload_details = self._tekdrive.get(ENDPOINTS["file_members"].format(file_id=self.id))
            self._upload_url = upload_details["upload_url"]

        # do single upload
        self._upload_to_storage(self._upload_url, file)
