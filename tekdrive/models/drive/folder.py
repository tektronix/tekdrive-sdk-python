"""Provides the Folder class."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, IO, Optional, List, Union

from ...routing import Route, ENDPOINTS
from ...utils.casing import to_snake_case
from .base import DriveBase
from ...exceptions import ClientException
from ...enums import ObjectType
from .member import Member
from ..permissions import Permissions
from .user import PartialUser

if TYPE_CHECKING:
    from .. import TekDrive


class Folder(DriveBase):
    """
    A class representing a TekDrive folder.

    Examples:
        Load a folder by id::

            folder_id = "3b525331-9da7-4e8d-b045-4acdba8d9dc7"
            folder = td.folder(folder_id)

    Attributes:
        created_at (datetime): When the folder was created.
        creator (:ref:`partial_user`): Folder creator.
        id (str): Unique ID of the folder.
        folder_type (str): Folder type such as ``"STANDARD"``, ``"PERSONAL"``, or ``"SHARES"``.
        name (str): Name of the folder.
        owner (:ref:`partial_user`): Folder owner.
        parent_folder_id (str): Unique ID of the folder's parent folder.
        shared_at (datetime, optional): When the folder was shared with the
            requesting user. Will be ``None`` if the user has direct access.
        type (str): Type of TekDrive object - will always be ``"FOLDER"``.
        permissions (:ref:`permissions`): Folder permissions for the requesting user.
        updated_at (datetime, optional): When the folder was last updated.
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
        else:
            fetched = True

        super().__init__(tekdrive, _data=_data, _fetched=fetched)

    def __setattr__(
        self,
        attribute: str,
        value: Union[str, int, "Member"],
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
        route = Route("GET", ENDPOINTS["folder_details"], folder_id=self.id)
        return self._tekdrive.request(route, should_parse=False)

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
        """
        Get a list of folder members.

        Examples:
            Iterate over all folder members::

                for member in folder.members():
                    print(member.username)
        """
        route = Route("GET", ENDPOINTS["folder_members"], folder_id=self.id)
        members = self._tekdrive.request(route)
        members._parent = self
        return members

    def move(self, parent_folder_id: str) -> None:
        """
        Move folder.

        Args:
            parent_folder_id: Unique ID of another folder to move the folder into.

        Examples:
            Move by ID::

                new_parent_folder_id = "1ae7fa38-9759-49f1-9e41-28a190b96023"
                folder.move(new_parent_folder_id)

            Move to newly created folder::

                new_parent_folder = td.folder.create("FolderA")
                folder.move(new_parent_folder.id)
        """
        data = dict(parentFolderId=parent_folder_id)
        self._update_details(data)
        self.parent_folder_id = parent_folder_id

    def save(self) -> None:
        """
        Save any changes to folder meta. Supported attributes: ``name``.

        Examples:
            Rename a folder::

                folder.name = "my_new_name"
                folder.save()
        """
        data = dict(name=self.name)
        self._update_details(data)

    def add_member(
        self, username: str = None, user_id: str = None, edit_access: bool = False
    ) -> Member:
        """
        Share the folder with an existing or new user.

        Args:
            username: The username (email) of the sharee.
            user_id: The user ID of the sharee.
            edit_access: Give member edit access?

        Examples:
            Share with read only permissions (default)::

                folder_member = folder.add_member(username="read_only@example.com")

            Share with edit permissions::

                folder_member = folder.add_member(user_id="354bcafb-6c54-4a1f-9b94-a76f38b548e5", edit_access=True)

        """
        data = dict(permissions=dict(read=True, edit=edit_access))
        if user_id:
            data["id"] = user_id
        elif username:
            data["username"] = username
        else:
            raise ClientException("Must supply `username` or `user_id`.")

        route = Route("POST", ENDPOINTS["folder_members"], folder_id=self.id)
        return self._tekdrive.request(route, json=data)

    def remove_member(self, user_id: str) -> None:
        """
        Revoke access for a current folder member.

        Args:
            user_id: The user ID of the member.

        Examples:
            Remove member::

                folder.remove_member(user_id="354bcafb-6c54-4a1f-9b94-a76f38b548e5")

        """
        route = Route(
            "DELETE", ENDPOINTS["folder_member"], folder_id=self.id, member_id=user_id
        )
        self._tekdrive.request(route)

    def modify_member(self, user_id: str, edit_access: bool) -> Member:
        """
        Modify an existing folder member.

        Args:
            user_id: The user ID of the member.
            edit_access: Give member edit access?

        Examples:
            Grant edit access::

                updated_folder_member = folder.modify_member(user_id="354bcafb-6c54-4a1f-9b94-a76f38b548e5", edit_access=True)

            Revoke edit access::

                updated_folder_member = folder.modify_member(user_id="354bcafb-6c54-4a1f-9b94-a76f38b548e5", edit_access=False)

        """
        route = Route(
            "PUT", ENDPOINTS["folder_member"], folder_id=self.id, member_id=user_id
        )
        data = dict(permissions=dict(read=True, edit=edit_access))
        return self._tekdrive.request(route, json=data)

    def upload(self, path_or_readable: Union[str, IO], file_name: str):
        """
        Create a new file and automatically upload its contents directly into this folder.

        Args:
            path_or_readable: Path to a local file or a readable stream
                representing the contents to upload.
            file_name (optional): Name of the new file.

        Raises:
            ClientException: If invalid file path is given.

        Examples:
            Upload using path::

                here = os.path.dirname(__file__)
                contents_path = os.path.join(here, "test_file_overwrite.txt")
                folder.upload(contents_path, "my_new_file")

            Upload using readable stream::

                with open("./test_file.txt"), "rb") as f:
                    folder.upload(f)
        """
        return self._tekdrive.file.create(
            path_or_readable, name=file_name, parent_folder_id=self.id
        )
