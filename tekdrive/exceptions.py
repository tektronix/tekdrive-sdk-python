class TekDriveException(Exception):
    """The base TekDrive Exception that all other exception classes extend."""


class TekDriveAPIException(TekDriveException):
    def __init__(
        self,
        data: dict,
        *optional_args: str,
    ):
        self.data = data

    @property
    def error_code(self) -> str:
        return self.data.get("error_code")

    @property
    def message(self) -> str:
        return self.data.get("message")

    @property
    def errors(self):
        return self.data.get("errors")


class TekDriveStorageException(TekDriveException):
    """Indicate exceptions that happen uploading/downloading from storage."""


class ClientException(TekDriveException):
    """Indicate exceptions that happen client side."""
