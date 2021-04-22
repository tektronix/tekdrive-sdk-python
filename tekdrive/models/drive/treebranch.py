"""Provides the Treebranch class."""
from typing import TYPE_CHECKING, Optional, Dict, Any, Union

from .base import DriveBase
from .file import File
from .folder import Folder

if TYPE_CHECKING:
    from .. import TekDrive


class Treebranch(DriveBase):
    """
    Represents a file or folder that is a branch in the tree.

    Attributes:
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
        if attribute == "children" and value.get("type") == "FILE":
            value = File(self._tekdrive, value["id"], _data=value)
        elif attribute == "children" and value.get("type") == "FOLDER":
            value = Folder(self._tekdrive, value["id"], _data=value)
        super().__setattr__(attribute, value)
