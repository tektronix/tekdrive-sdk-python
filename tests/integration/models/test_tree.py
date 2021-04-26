import pytest, json
from tekdrive.utils.casing import to_snake_case, to_camel_case
from tekdrive.exceptions import TekDriveAPIException
from tekdrive.models import Tree
from tekdrive.enums import FolderType, ObjectType

from ..base import IntegrationTest

@pytest.mark.integration
class TestTree(IntegrationTest):
    def test_get_tree(self, tekdrive_vcr):
        results = Tree(self.tekdrive).get()
        assert results.type == ObjectType.FOLDER

    def test_get_tree_folder_id(self,tekdrive_vcr):
        folder_id = '61264d17-fba1-4676-bbcc-b46c1f0ddd4c'
        results = Tree(self.tekdrive).get(folder_id=folder_id)
        assert results.id == folder_id

    def test_get_tree_silo(self,tekdrive_vcr):
        silo = 'SHARES'
        results = Tree(self.tekdrive).get(silo=silo)
        assert results.folder_type == FolderType.SHARES

    def test_tree_terminating_node_returns_empty_list(self,tekdrive_vcr):
        # TODO:
        pass

    def test_get_tree_folders_only(self,tekdrive_vcr):
        # TODO:
        # only return folders
        # folders_only = True
        # results = Tree(self.tekdrive).get(folders_only=folders_only)
        # for result in results._children:
        #   assert result.type==ObjectType.FOLDER
        pass

    def test_get_tree_include_trashed(self,tekdrive_vcr):
        # include trash in return
        include_trashed = True
        expected_number_of_children = 6
        results = Tree(self.tekdrive).get(include_trashed=include_trashed)
        assert sum(1 for _ in results._children) == expected_number_of_children

    def test_tree_get_forbidden(self, tekdrive_vcr):
        with pytest.raises(TekDriveAPIException) as e:
            results = Tree(self.tekdrive).get()
        assert e.value.error_code == "FORBIDDEN"
