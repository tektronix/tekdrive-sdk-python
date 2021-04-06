from enum import Enum


class SharingType(Enum):
    UNLIMITED = "UNLIMITED"
    PERMISSIONS_LIMITED = "PERMISSIONS_LIMITED"
    DISABLED = "DISABLED"


class ObjectType(Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"


class FolderType(Enum):
    STANDARD = "STANDARD"
    SHARES = "SHARES"
    PERSONAL = "PERSONAL"


class ErrorCode(Enum):
    FILE_GONE = "FILE_GONE"
