"""Provides the User class."""
from typing import TYPE_CHECKING, Optional, Dict, Any

# from ..endpoints import ENDPOINTS
from .base import TekDriveBase

if TYPE_CHECKING:  # pragma: no cover
    from .. import Client


class Member(TekDriveBase):
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
        super().__init__(client, _data=None)
