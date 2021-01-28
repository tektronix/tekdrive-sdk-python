"""Provides the User class."""
from typing import TYPE_CHECKING, Any, Dict, IO, Optional, List, Union

from ...endpoints import ENDPOINTS
from ...utils.casing import to_snake_case
from .base import DriveBase
from .member import Member

if TYPE_CHECKING:  # pragma: no cover
    from .. import Client


class File(DriveBase):
    STR_FIELD = "id"

    def __init__(
        self,
        client: "Client",
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

        super().__init__(client, _data=_data, _fetched=fetched)

    def __setattr__(
        self,
        attribute: str,
        value: Union[str, int, "Member"],
    ):
        """Parse owner and creator into members."""
        if attribute == "owner" or attribute == "creator":
            print(f"attr {attribute}, value {value}")
            value = Member.from_data(self._client, value)
        super().__setattr__(attribute, value)

    def _fetch_info(self):
        return "file_details", {"file_id": self.id}, {}

    def _fetch_data(self):
        name, fields, params = self._fetch_info()
        path = ENDPOINTS[name].format(**fields)
        return self._client.request("GET", path, params)

    def _fetch(self):
        data = self._fetch_data()
        data = to_snake_case(data)
        other = type(self)(self._client, _data=data)
        self.__dict__.update(other.__dict__)
        print(self.__dict__)
        self._fetched = True

    @staticmethod
    def _create(
        _client,
        name=None,
    ):
        data = dict(name=name)
        new_file = _client.post(ENDPOINTS["file_create"], json=data)
        return new_file

    def members(self) -> List[Member]:
        """Return a list of file members"""
        return self._client.get(ENDPOINTS["file_members"].format(file_id=self.id))

    def upload(self, file: IO):
        if self._upload_url is None:
            upload_details = self._client.get(ENDPOINTS["file_members"].format(file_id=self.id))
            self._upload_url = upload_details["upload_url"]

        # TODO: do we need headers={"Content-Type": "application/octet-stream"} ?
        self._client.request("PUT", self._upload_url, data=file)
