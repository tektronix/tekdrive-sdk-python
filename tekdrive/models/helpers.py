from typing import IO, Union

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
        path_or_readable: Union[str, IO] = None,
        name: str = None,
        parent_folder_id: str = None,
    ) -> File:
        """Create a new file.
        """
        if path_or_readable is None and name is None:
            raise ClientException("Must supply `path_or_readable` or `name`")

        new_file = File._create(
            _tekdrive=self._tekdrive,
            path_or_readable=path_or_readable,
            name=name,
            parent_folder_id=parent_folder_id,
        )
        return new_file
