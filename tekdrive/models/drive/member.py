"""Provides the User class."""
from typing import TYPE_CHECKING, Optional, Dict, Any

from .base import DriveBase
from ..base import BaseList

if TYPE_CHECKING:  # pragma: no cover
    from .. import TekDrive


class Member(DriveBase):
    STR_FIELD = "id"

    @classmethod
    def from_data(cls, tekdrive, data):
        if data == "[deleted]":
            return None
        return cls(tekdrive, data)

    def __init__(
        self,
        tekdrive: "TekDrive",
        _data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(tekdrive, _data=_data)


class MembersList(BaseList):
    """List of members"""

    CHILD_ATTRIBUTE = "members"
