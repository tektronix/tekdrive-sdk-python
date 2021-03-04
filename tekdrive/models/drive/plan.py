"""Provides the Plan class."""
from typing import TYPE_CHECKING, Optional, Dict, Any

from .base import DriveBase
from ...enums import SharingType

if TYPE_CHECKING:
    from .. import TekDrive


class Plan(DriveBase):
    """
    Represents a TekDrive plan.

    Attributes:
        id (str): Unique ID of the plan.
        name (str): Plan name.
        limits (dict): Raw limits for the plan such as storage limit,
            access key limit, and sharing type.
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

    @property
    def access_key_limit(self) -> int:
        """
        The number of access keys allowed by the plan.
        """
        return self.limits.get("access_key_limit")

    @property
    def sharing_type(self) -> SharingType:
        """
        The plan sharing type.
        """
        return SharingType(self.limits["sharing_type"])

    @property
    def storage_limit(self) -> int:
        """
        The plan storage limit in bytes.
        """
        return int(self.limits["storage_size_limit"])
