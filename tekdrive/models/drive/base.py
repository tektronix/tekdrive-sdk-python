"""Provide the DriveBase class."""
import os
import requests
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, IO, Optional, Union

from ..base import TekDriveBase
from ...exceptions import ClientException, TekDriveStorageException

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


class Downloadable(ABC):
    """Abstract base class for download functionality."""

    @abstractmethod
    def _fetch_download_url(self):
        pass

    def _download_from_storage(self):
        download_url = self._fetch_download_url()
        try:
            r = requests.get(
                download_url,
            )
            r.raise_for_status()
            return r.content
        except requests.exceptions.HTTPError as exception:
            raise TekDriveStorageException("Upload failed") from exception

    def download(self, path_or_writable: Union[str, IO] = None) -> None:
        """
        Download contents.

        Args:
            path_or_writable: Path to a local file or a writable stream
                where contents will be written.

        Raises:
            ClientException: If invalid file path is given.

        Examples:
            Download to local file using path::

                here = os.path.dirname(__file__)
                contents_path = os.path.join(here, "test_file_overwrite.txt")
                file.download(contents_path)

            Download using writable stream::

                with open("./download.csv", "wb") as f:
                    file.download(f)
        """
        if path_or_writable is None:
            # return content directly
            return self._download_from_storage()

        if isinstance(path_or_writable, str):
            file_path = path_or_writable

            if not os.path.exists(file_path):
                raise ClientException(f"File '{file_path}' does not exist.")

            with open(file_path, "wb") as file:
                file.write(self._download_from_storage())
        else:
            writable = path_or_writable
            writable.write(self._download_from_storage())
