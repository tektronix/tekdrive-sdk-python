"""Provides the User class."""
from typing import TYPE_CHECKING, Optional, Dict, Any

# from ..endpoints import ENDPOINTS
from .base import DriveBase
from ..base import BaseList

if TYPE_CHECKING:  # pragma: no cover
    from .. import Client


class Member(DriveBase):
    STR_FIELD = "id"

    @classmethod
    def from_data(cls, client, data):
        if data == "[deleted]":
            return None
        return cls(client, data)

    def __init__(
        self,
        client: "Client",
        _data: Optional[Dict[str, Any]] = None,
    ):
        print(f'member data {_data}')
        super().__init__(client, _data=_data)
        print(f'member dict {self.__dict__}')

    # def __str__(self):
    #     return f"Member<{self.id}>"


class MembersList(BaseList):
    """List of members"""

    CHILD_ATTRIBUTE = "members"
