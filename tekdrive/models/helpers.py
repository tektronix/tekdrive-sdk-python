from .base import TekDriveBase
from .drive.file import File


class FileHelper(TekDriveBase):

    def __call__(self, id: str) -> File:
        """Return a lazy instance of :class:`~.File`.

        :param name: The name of the file.
        """
        return File(self._client, id=id)

    def create(
        self,
        name: str,
    ) -> File:
        """Create a new file.

        :param name: The name for the new file.
        """
        new_file = File._create(
            _client=self._client,
            name=name,
        )
        print(f"FileHelper.create new_file {new_file}")
        return new_file
