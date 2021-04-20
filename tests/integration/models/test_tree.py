import pytest, json
from tekdrive.utils.casing import to_snake_case, to_camel_case
from tekdrive.models import Tree

from ..base import IntegrationTest

# @pytest.mark.integration
# class TestTree(IntegrationTest):
    # def test_get_tree(self, tekdrive_vcr):
    #     results = Tree(self.tekdrive).get()
    #     # for idx, result in enumerate(results):
    #     #     assert len(result.tree) > 0
    #     # assert idx > 0
    #     assert len(results["tree"])> 0

    # def test_get_tree_folder_id(self,tekdrive_vcr):
    #     # Use folderId param

    # def test_get_tree_silo(self,tekdrive_vcr):
    #     # Use personal/shares silo

    # def test_get_tree_depth(self,tekdrive_vcr):
    #     # control levels returned

    # def test_get_tree_folders_only(self,tekdrive_vcr):
    #     # only return folders

    # def test_get_tree_include_trashed(self,tekdrive_vcr):
    #     # include trash in return