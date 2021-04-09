import pytest

from tekdrive.models import Trashcan, File, Folder

from ..base import IntegrationTest


@pytest.mark.integration
class TestTrash(IntegrationTest):
    # def test_trash_was_emptied(self, tekdrive_vcr):
    #     
    #     assert len(results_list) == 0

    # def test_trash_empty_forbidden(self, tekdrive_vcr):
    #     
    #     assert e.value.error_code == "FORBIDDEN"

    def test_list_of_trash(self, tekdrive_vcr):
        results = Trashcan(self.tekdrive).get()
        for idx, result in enumerate(results):
            assert len(result.trasher) > 0
        assert idx > 0

    def test_list_of_trash_created_at(self, tekdrive_vcr):
        results = Trashcan(self.tekdrive).get(order_by="createdAt")
        for idx, result in enumerate(results):
            #assert date[1] is later than date[0]
        assert idx > 0

    # def test_list_of_trash_updated_at(self, tekdrive_vcr):


    # def test_list_of_trash_total_bytes(self, tekdrive_vcr):


    # def test_list_of_trash_limit(self, tekdrive_vcr):


    # def test_trash_get_forbidden(self, tekdrive_vcr):