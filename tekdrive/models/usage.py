"""Provides the Usage dataclass."""
from dataclasses import dataclass


@dataclass
class Usage:
    """
    Represents TekDrive usage details and stats.
    """

    total_bytes_owned: str
    files_owned_count: int
    total_bytes_owned_in_trash: str
    files_owned_in_trash_count: int
    total_bytes_created: str
    files_created_count: int
    storage_size_limit: str

    @property
    def storage_limit(self) -> int:
        """
        The total limit in bytes of the user's storage space.
        """
        return int(self.storage_size_limit)

    @property
    def storage_freeable(self) -> int:
        """
        The total number of bytes counting against the user's storage limit that
        are in the trash and can be freed by emptying the trash.
        """
        return int(self.total_bytes_owned_in_trash)

    @property
    def storage_used(self) -> int:
        """
        The current number of bytes counting against the user's storage limit.
        """
        return int(self.total_bytes_owned)

    @property
    def storage_remaining(self) -> int:
        """
        The total number of bytes of storage available.
        """
        return self.storage_limit - self.storage_used
