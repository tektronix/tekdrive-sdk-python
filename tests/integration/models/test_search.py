import pytest

from tekdrive.exceptions import ClientException
from tekdrive.models import Search, File, Folder

from ..base import IntegrationTest


@pytest.mark.integration
class TestSearch(IntegrationTest):

    def test_file_only_search(self, tekdrive_vcr):
        name = "new_"
        results = Search(self.tekdrive).query(name=name, include_files=True, include_folders=False)
        for result in results:
            assert isinstance(result, File)
            assert name in result.name.lower()

    def test_folder_only_search(self, tekdrive_vcr):
        name = "new"
        results = Search(self.tekdrive).query(name=name, include_files=False, include_folders=True)
        for result in results:
            assert isinstance(result, Folder)
            assert name in result.name.lower()
