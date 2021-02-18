"""Provides the User class."""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Union

from ..routing import Route, ENDPOINTS
from .base import TekDriveBase

if TYPE_CHECKING:  # pragma: no cover
    from .. import TekDrive


@dataclass
class PartialUser:
    """
    Represents a simple User which provides a subset of a full User's attributes.

    Attributes:
        id (str): Unique ID for the user
        username (str): Username for the user
    """
    id: str
    username: str


class User(TekDriveBase):
    def __init__(self, tekdrive: "TekDrive"):
        super().__init__(tekdrive, _data=None)
