import pytest
from tekdrive.utils.casing import to_snake_case, to_camel_case
from tekdrive.models import Trashcan, File, Folder

from ..base import IntegrationTest

@pytest.mark.integration
class TestTrash(IntegrationTest):
    def test_trash_was_emptied(self, tekdrive_vcr):
        Trashcan(self.tekdrive).empty()
        results = Trashcan(self.tekdrive).get()
        for idx, result in enumerate(results):
            assert len(result.trasher) == 0

    # def test_trash_empty_forbidden(self, tekdrive_vcr):
    #     TODO: need a forbidden trashcan
    #     assert e.value.error_code == "FORBIDDEN"

    def test_list_of_trash(self, tekdrive_vcr):
        results = Trashcan(self.tekdrive).get()
        for idx, result in enumerate(results):
            assert len(result.trasher) > 0
        assert idx > 0

    def test_list_of_trash_created_at(self, tekdrive_vcr):
        results = Trashcan(self.tekdrive).get(order_by="createdAt")
        dates = []
        for idx, result in enumerate(results):
            dates.append(result.item.created_at)
        assert dates[1] > dates[0]

    def test_list_of_trash_updated_at(self, tekdrive_vcr):
        results = Trashcan(self.tekdrive).get(order_by="updatedAt")
        dates = []
        for idx, result in enumerate(results):
            dates.append(result.item.updated_at)
        assert dates[1] > dates[0]

    def test_list_of_trash_trashed_at(self, tekdrive_vcr):
        results = Trashcan(self.tekdrive).get(order_by="trashedAt")
        dates = []
        for idx, result in enumerate(results):
            dates.append(result.trashed_at)
        assert dates[1] > dates[0]

    def test_list_of_trash_total_bytes(self, tekdrive_vcr):
        results = Trashcan(self.tekdrive).get(order_by="totalBytes")
        bytes = []
        for idx, result in enumerate(results):
            bytes.append(result.total_bytes)
        assert bytes[1] >= bytes[0]

    def test_list_of_trash_limit(self, tekdrive_vcr):
        results = Trashcan(self.tekdrive).get(limit=3)
        for idx, result in enumerate(results):
            assert len(result.trasher) > 0
        assert idx == 2

    # def test_trash_get_forbidden(self, tekdrive_vcr):
        # TODO: need a forbidden trashed item
        # assert e.value.error_code == "FORBIDDEN"