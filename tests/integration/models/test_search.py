import pytest

from tekdrive.models import Search, File, Folder

from ..base import IntegrationTest


@pytest.mark.integration
class TestSearch(IntegrationTest):
    def test_query_returns_nothing(self, tekdrive_vcr):
        name = "name_of_things_that_dont_even_exist"
        results = Search(self.tekdrive).query(name=name)
        results_list = list(results)
        assert len(results_list) == 0

    def test_query_files_only(self, tekdrive_vcr):
        name = "new_"
        results = Search(self.tekdrive).query(
            name=name, include_files=True, include_folders=False
        )
        for result in results:
            assert isinstance(result, File)
            assert name in result.name.lower()

    def test_query_folders_only(self, tekdrive_vcr):
        name = "new"
        results = Search(self.tekdrive).query(
            name=name, include_files=False, include_folders=True
        )
        for result in results:
            assert isinstance(result, Folder)
            assert name in result.name.lower()

    def test_files_name_search_in_personal(self, tekdrive_vcr):
        name = "test"
        personal_silo_folder_id = "a63a781f-ecbc-442f-b053-c5bd65ef611b"
        results = Search(self.tekdrive).files(name=name, silo="personal")
        for result in results:
            assert isinstance(result, File)
            assert name in result.name.lower()
            assert result.parent_folder_id == personal_silo_folder_id

    def test_files_name_search_in_personal_with_limit(self, tekdrive_vcr):
        name = "test"
        limit = 5
        personal_silo_folder_id = "a63a781f-ecbc-442f-b053-c5bd65ef611b"
        results = Search(self.tekdrive).files(name=name, silo="personal", limit=limit)
        for idx, result in enumerate(results):
            assert isinstance(result, File)
            assert name in result.name.lower()
            assert result.parent_folder_id == personal_silo_folder_id
        assert idx + 1 <= limit

    def test_folders_name_search_in_personal(self, tekdrive_vcr):
        name = "new"
        personal_silo_folder_id = "a63a781f-ecbc-442f-b053-c5bd65ef611b"
        results = Search(self.tekdrive).folders(name=name, silo="personal")
        for result in results:
            assert isinstance(result, Folder)
            assert name in result.name.lower()
            assert result.parent_folder_id == personal_silo_folder_id

    def test_folders_name_search_in_personal_with_limit(self, tekdrive_vcr):
        name = "new"
        limit = 1
        personal_silo_folder_id = "a63a781f-ecbc-442f-b053-c5bd65ef611b"
        results = Search(self.tekdrive).folders(name=name, silo="personal", limit=limit)
        for idx, result in enumerate(results):
            assert isinstance(result, Folder)
            assert name in result.name.lower()
            assert result.parent_folder_id == personal_silo_folder_id
        assert idx + 1 <= limit

    def test_query_include_trash(self, tekdrive_vcr):
        name = "Bark"
        results = Search(self.tekdrive).query(
            name=name, include_trashed=True
        )
        for idx, result in enumerate(results):
            assert name.lower() in result.name.lower()
        assert idx + 1 == 3
