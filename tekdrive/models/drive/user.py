"""Provides the User class."""
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any, Union

from .base import DriveBase
from .plan import Plan

if TYPE_CHECKING:
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


class DriveUser(DriveBase):
    """
    Represents a TekDrive full user.

    Attributes:
        id (str): Unique user ID.
        username (str): Username (email) of the user.
        account_id (str): TekDrive account ID for the user.
        created_at (datetime): When the user account was created.
        updated_at (datetime): When the user account was updated.
        plan (:ref:`plan`): Plan details for the user.
    """

    STR_FIELD = "id"

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
        if attribute == "plan":
            value = Plan.from_data(self._tekdrive, value)
        elif attribute in ("created_at", "updated_at", "shared_at"):
            if value is not None:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        super().__setattr__(attribute, value)
