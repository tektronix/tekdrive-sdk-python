"""Provides the Member class."""
from typing import TYPE_CHECKING, Optional, Dict, Any, Union

from .base import DriveBase
from ..base import BaseList
from ..permissions import Permissions

if TYPE_CHECKING:
    from .. import TekDrive


class Member(DriveBase):
    """
    Represents a user who has access to a TekDrive file or folder along
    with their permissions for that object.

    Attributes:
        id (str): Unique user ID
        username (str): Username of the member
        permissions (:ref:`permissions`): Member permissions
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
        if attribute == "permissions":
            value = Permissions(**value)
        super().__setattr__(attribute, value)


class MembersList(BaseList):
    """List of members"""

    _parent = None

    LIST_ATTRIBUTE = "members"
