"""Provide the DriveBase class."""
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ..base import TekDriveBase

if TYPE_CHECKING:
    from ... import TekDrive


class DriveBase(TekDriveBase):
    """Base class that represents actual TekDrive objects."""

    def __init__(
        self,
        tekdrive: "TekDrive",
        _data: Optional[Dict[str, Any]],
        _fetched: bool = False,
    ):
        """
        Initialize a DriveBase instance (or a subclass).

        Args:
            tekdrive: An instance of TekDrive.

        """
        super().__init__(tekdrive, _data=_data)
        self._fetched = _fetched
        if self.STR_FIELD not in self.__dict__:
            raise ValueError(f"An invalid value was specified for `{self.STR_FIELD}`.")

    def __eq__(self, other: Union[Any, str]) -> bool:
        """Return whether the other instance equals the current."""
        if isinstance(other, str):
            return other.lower() == str(self).lower()
        return (
            isinstance(other, self.__class__)
            and str(self).lower() == str(other).lower()
        )

    def __getattr__(self, attribute: str) -> Any:
        """Return the value of `attribute`."""
        if not attribute.startswith("_") and not self._fetched:
            self._fetch()
            return getattr(self, attribute)
        raise AttributeError(
            f"{self.__class__.__name__!r} object has no attribute {attribute!r}"
        )

    def __hash__(self) -> int:
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self).lower())

    def __repr__(self) -> str:
        """Return an object initialization representation of the instance."""
        return f"{self.__class__.__name__}({self.STR_FIELD}={str(self)!r})"

    def __str__(self) -> str:
        """Return a string representation of the instance."""
        return getattr(self, self.STR_FIELD)

    def __ne__(self, other: Any) -> bool:
        """Return whether the other instance differs from the current."""
        return not self == other

    def _fetch(self):
        self._fetched = True

    def _reset_attributes(self, *attributes):
        for attribute in attributes:
            if attribute in self.__dict__:
                del self.__dict__[attribute]
        self._fetched = False
