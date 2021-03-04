from enum import Enum


class SharingType(Enum):
    UNLIMITED = "UNLIMITED"
    PERMISSIONS_LIMITED = "PERMISSIONS_LIMITED"
    DISABLED = "DISABLED"


class ObjectType(Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"

# TODO: Folder types (STANDARD, SHARES, PERSONAL)
