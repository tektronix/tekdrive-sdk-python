from enum import Enum


class SharingType(Enum):
    unlimited = "UNLIMITED"
    permissions_limited = "PERMISSIONS_LIMITED"
    disabled = "DISABLED"


# TODO: Object types (FILE and FOLDER)
# TODO: Folder types (STANDARD, SHARES, PERSONAL)
