from .base import TekDriveBase
from .drive.file import File
from ..exceptions import ClientException


class FileHelper(TekDriveBase):

    def __call__(self, id: str) -> File:
        """Return a lazy instance of :class:`~.File`.

        :param name: The name of the file.
        """
        return File(self._tekdrive, id=id)

    def create(
        self,
        file_path: str = None,
        name: str = None,
    ) -> File:
        """Create a new file.
        """
        if file_path is None and name is None:
            raise ClientException("Must supply `file_path` or `name`")

        new_file = File._create(
            _tekdrive=self._tekdrive,
            file_path=file_path,
            name=name,
        )
        print(f"FileHelper.create new_file {new_file}")
        return new_file
