"""Provides the Member class."""
from typing import TYPE_CHECKING, Optional, Dict, Any, Union

from .base import DriveBase
from .file import File
from .folder import Folder

if TYPE_CHECKING:
    from .. import TekDrive


class Trash(DriveBase):
    """
    Represents a file or folder that has been placed in the trashcan.

    Attributes:
        trasher (PartialUser): The user who placed the object in the trash.
        trashed_at (datetime): When the object was placed in the trash.
        trashed_directly (bool): Was the item placed directly in the trash?
        total_bytes (str): The total bytes of the trashed object. If the item is
            a folder, this will be the total sum of the folder contents.
        item_share_count (int): How many TekDrive users the item is shared with.
        item (:ref:`file` or :ref:`folder`): File or folder details.
    """

    STR_FIELD = "id"

    @classmethod
    def from_data(cls, tekdrive, data):
        return cls(tekdrive, data)

    def __init__(
        self,
        tekdrive: "TekDrive",
        _data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(tekdrive, _data=_data)

    def __setattr__(
        self,
        attribute: str,
        value: Union[str, int, Dict[str, Any]],
    ):
        if attribute == "item" and value.get("type") == "FILE":
            value = File(self._tekdrive, value["id"], _data=value)
        elif attribute == "item" and value.get("type") == "FOLDER":
            value = Folder(self._tekdrive, value["id"], _data=value)
        super().__setattr__(attribute, value)
