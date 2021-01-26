"""Provides the User class."""
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Union

from ..endpoints import ENDPOINTS
from .base import TekDriveBase

if TYPE_CHECKING:  # pragma: no cover
    from .. import Client


class User(TekDriveBase):
    def __init__(self, client: "Client"):
        super().__init__(client, _data=None)
