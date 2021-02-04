"""Provides the File class."""
import os
import requests
from typing import TYPE_CHECKING, Any, Dict, IO, Optional, List, Union

from ...routing import Route, ENDPOINTS
from ...exceptions import ClientException, TekDriveStorageException
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
        _data: Optional[Dict[str, Any]] = None,
    ):
        fetched = False
        if id:
            self.id = id
        elif _data:
            fetched = True
        else:
            raise ClientException("Must supply `id` or `_data`.")

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
        route = Route('GET', ENDPOINTS["file_details"], file_id=self.id)
        return self._tekdrive.request(route, objectify=False)

    def _fetch(self):
        data = self._fetch_data()
        other = type(self)(self._tekdrive, _data=to_snake_case(data))
        self.__dict__.update(other.__dict__)
        self._fetched = True

    def _fetch_upload_url(self):
        route = Route("GET", ENDPOINTS["file_upload"], file_id=self.id)
        upload_details = self._tekdrive.request(route)
        return upload_details["upload_url"]

    def _fetch_download_url(self):
        route = Route("GET", ENDPOINTS["file_download"], file_id=self.id)
        download_details = self._tekdrive.request(route)
        return download_details["download_url"]

    def _update_details(self, data):
        route = Route("PUT", ENDPOINTS["file_details"], file_id=self.id)
        return self._tekdrive.request(route, json=data)

    def _upload_to_storage(self, file: IO):
        # we may already have upload url from file creation
        if self._upload_url is None:
            self._upload_url = self._fetch_upload_url()

        try:
            r = requests.put(
                self._upload_url,
                data=file,
                headers={
                    "Content-Type": "application/octet-stream",
                },
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as exception:
            raise TekDriveStorageException("Upload failed") from exception

    def _download_from_storage(self):
        download_url = self._fetch_download_url()
        try:
            r = requests.get(
                download_url,
            )
            r.raise_for_status()
            return r.content
        except requests.exceptions.HTTPError as exception:
            raise TekDriveStorageException("Upload failed") from exception

    @staticmethod
    def _create(
        _tekdrive,
        path_or_readable: Union[str, IO] = None,
        name: str = None,
        parent_folder_id: str = None,
    ) -> "File":
        if path_or_readable and name is None:
            # get name from path or readable
            if isinstance(path_or_readable, str):
                name = os.path.basename(path_or_readable)
            else:
                name = os.path.basename(path_or_readable.name)

        data = dict(name=name, parentFolderId=parent_folder_id)
        route = Route("POST", ENDPOINTS["file_create"])
        new_file = _tekdrive.request(route, json=data)

        if path_or_readable:
            new_file.upload(path_or_readable)

        return new_file

    def members(self) -> List[Member]:
        """Return a list of file members"""
        route = Route("GET", ENDPOINTS["file_members"], file_id=self.id)
        return self._tekdrive.request(route)

    def upload(self, path_or_readable: Union[str, IO]) -> None:
        # TODO: multipart upload support
        if isinstance(path_or_readable, str):
            file_path = path_or_readable

            if not os.path.exists(file_path):
                raise ClientException(f"File '{file_path}' does not exist.")

            with open(file_path, "rb") as file:
                self._upload_to_storage(file)
        else:
            readable = path_or_readable
            self._upload_to_storage(readable)

    def download(self, path_or_writable: Union[str, IO] = None):
        if path_or_writable is None:
            # return content directly
            return self._download_from_storage()

        if isinstance(path_or_writable, str):
            file_path = path_or_writable

            if not os.path.exists(file_path):
                raise ClientException(f"File '{file_path}' does not exist.")

            with open(file_path, "wb") as file:
                file.write(self._download_from_storage())
        else:
            writable = path_or_writable
            writable.write(self._download_from_storage())

    def move(self, parent_folder_id: str) -> None:
        data = dict(parentFolderId=parent_folder_id)
        self._update_details(data)
        self.parent_folder_id = parent_folder_id

    def save(self) -> None:
        data = dict(name=self.name)
        self._update_details(data)

    def share(self, username: str, edit: bool = False) -> Member:
        route = Route("POST", ENDPOINTS["file_members"], file_id=self.id)
        data = {
            "username": username,
            "permissions": dict(read=True, edit=edit)
        }
        return self._tekdrive.request(route, json=data)
