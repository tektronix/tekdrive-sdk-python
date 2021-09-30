"""Provides the File class."""
import os
import requests
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, IO, Optional, Union

from ...routing import Route, ENDPOINTS
from ...exceptions import ClientException, TekDriveStorageException
from ...utils.casing import to_snake_case, to_camel_case
from .base import DriveBase
from .member import Member, MembersList
from .user import PartialUser
from ...enums import ObjectType
from ..permissions import Permissions

if TYPE_CHECKING:
    from .. import TekDrive


class File(DriveBase):
    """
    A class representing a TekDrive file.s

    Examples:
        Load a file by id::

            file_id = "9606be66-8af0-42fc-b199-7c0ca7e30d73"
            file = td.file(file_id)

    Attributes:
        bytes (str): File size in bytes.
        created_at (datetime): When the file was created.
        creator (:ref:`partial_user`): File creator.
        file_type (str): File type such as ``"JPG"`` or ``"WFM"``.
        id (str): Unique ID of the file.
        name (str): Name of the file.
        owner (:ref:`partial_user`): File owner.
        parent_folder_id (str): Unique ID of the file's parent folder.
        shared_at (datetime, optional): When the file was shared with the
            requesting user. Will be ``None`` if the user has direct access.
        type (str): Type of TekDrive object - will always be ``"FILE"``.
        permissions (:ref:`permissions`): File permissions for the requesting user.
        updated_at (datetime, optional): When the file was last updated.
    """

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
        value: Union[str, int, Dict[str, Any]],
    ):
        if attribute == "owner" or attribute == "creator":
            value = PartialUser(**value)
        elif attribute in ("created_at", "updated_at", "shared_at"):
            if value is not None:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        elif attribute == "permissions":
            value = Permissions(**value)
        elif attribute == "type":
            value = ObjectType(value)
        super().__setattr__(attribute, value)

    def _fetch_data(self):
        route = Route("GET", ENDPOINTS["file_details"], file_id=self.id)
        return self._tekdrive.request(route, should_parse=False)

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

    def members(self) -> MembersList:
        """
        Get a list of file members.

        Examples:
            Iterate over all file members::

                for member in file.members():
                    print(member.username)

        Returns:
            List [ :ref:`member` ]
        """
        route = Route("GET", ENDPOINTS["file_members"], file_id=self.id)
        members = self._tekdrive.request(route)
        members._parent = self
        return members

    def restore(self) -> None:
        """
        Restore the file from user's trashcan.

        Examples:
            Restore - remove from trash::

                file.restore()
        """
        route = Route("POST", ENDPOINTS["file_restore"], file_id=self.id)
        self._tekdrive.request(route)

    def delete(self, hard_delete: bool = False) -> None:
        """
        Delete the file, by default it will be placed in the user's trashcan.

        Args:
            hard_delete: Permanently delete the file?

        Examples:
            Delete - placing in trash::

                file.delete()

            Delete - immediately delete::

                file.delete(hard_delete=True)
        """
        params = to_camel_case(dict(hard_delete=hard_delete))

        route = Route("DELETE", ENDPOINTS["file_delete"], file_id=self.id)
        self._tekdrive.request(route, params=params)

    def upload(self, path_or_readable: Union[str, IO]) -> None:
        """
        Upload file contents. This will overwrite existing content, if any.

        Args:
            path_or_readable: Path to a local file or a readable stream
                representing the contents to upload.

        Raises:
            ClientException: If invalid file path is given.

        Examples:
            Upload using path::

                here = os.path.dirname(__file__)
                contents_path = os.path.join(here, "test_file_overwrite.txt")
                file.upload(contents_path)

            Upload using readable stream::

                with open("./test_file.txt"), "rb") as f:
                    new_file.upload(f)
        """
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

    def download(self, path_or_writable: Union[str, IO] = None) -> None:
        """
        Download file contents.

        Args:
            path_or_writable: Path to a local file or a writable stream
                where file contents will be written.

        Raises:
            ClientException: If invalid file path is given.

        Examples:
            Download to local file using path::

                here = os.path.dirname(__file__)
                contents_path = os.path.join(here, "test_file_overwrite.txt")
                file.download(contents_path)

            Download using writable stream::

                with open("./download.csv"), "wb") as f:
                    file.download(f)
        """
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
        """
        Move file to a different folder.

        Args:
            parent_folder_id: Unique ID of folder to move the file into.

        Examples:
            Move by ID::

                folder_id = "3b525331-9da7-4e8d-b045-4acdba8d9dc7"
                file.move(folder_id)

            Move to newly created folder::

                folder = td.folder.create("FolderA")
                file.move(folder.id)
        """
        data = dict(parentFolderId=parent_folder_id)
        self._update_details(data)
        self.parent_folder_id = parent_folder_id

    def save(self) -> None:
        """
        Save any changes to file meta. Supported attributes: ``name``.

        Examples:
            Rename a file::

                file.name = "my_new_name"
                file.save()
        """
        data = dict(name=self.name)
        self._update_details(data)

    def add_member(
        self, username: str = None, user_id: str = None, edit_access: bool = False
    ) -> Member:
        """
        Share the file with an existing or new user.

        Args:
            username: The username (email) of the sharee.
            user_id: The user ID of the sharee.
            edit_access: Give member edit access?

        Examples:
            Share with read only permissions (default)::

                file_member = file.add_member(username="read_only@example.com")

            Share with edit permissions::

                file_member = file.add_member(user_id="354bcafb-6c54-4a1f-9b94-a76f38b548e5", edit_access=True)

        Returns:
            :ref:`member`
        """
        data = dict(permissions=dict(read=True, edit=edit_access))
        if user_id:
            data["id"] = user_id
        elif username:
            data["username"] = username
        else:
            raise ClientException("Must supply `username` or `user_id`.")

        route = Route("POST", ENDPOINTS["file_members"], file_id=self.id)
        return self._tekdrive.request(route, json=data)

    def remove_member(self, user_id: str) -> None:
        """
        Revoke access for a current file member.

        Args:
            user_id: The user ID of the member.

        Examples:
            Remove member::

                file.remove_member(user_id="354bcafb-6c54-4a1f-9b94-a76f38b548e5")

        """
        route = Route(
            "DELETE", ENDPOINTS["file_member"], file_id=self.id, member_id=user_id
        )
        self._tekdrive.request(route)

    def modify_member(self, user_id: str, edit_access: bool) -> Member:
        """
        Modify an existing file member.

        Args:
            user_id: The user ID of the member.
            edit_access: Give member edit access?

        Examples:
            Grant edit access::

                updated_file_member = file.modify_member(user_id="354bcafb-6c54-4a1f-9b94-a76f38b548e5", edit_access=True)

            Revoke edit access::

                updated_file_member = file.modify_member(user_id="354bcafb-6c54-4a1f-9b94-a76f38b548e5", edit_access=False)

        Returns:
            :ref:`member`

        """
        route = Route(
            "PUT", ENDPOINTS["file_member"], file_id=self.id, member_id=user_id
        )
        data = dict(permissions=dict(read=True, edit=edit_access))
        return self._tekdrive.request(route, json=data)
