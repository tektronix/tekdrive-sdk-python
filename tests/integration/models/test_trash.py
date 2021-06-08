import pytest
from tekdrive.exceptions import ForbiddenAPIException
from tekdrive.models import Trashcan

from ..base import IntegrationTest


@pytest.mark.integration
class TestTrash(IntegrationTest):
    def test_trash_was_emptied(self, tekdrive_vcr):
        Trashcan(self.tekdrive).empty()
        results = Trashcan(self.tekdrive).get()
        assert sum(1 for _ in results) == 0

    def test_trash_empty_forbidden(self, tekdrive_vcr):
        with pytest.raises(ForbiddenAPIException) as e:
            Trashcan(self.tekdrive).empty()
        assert e.value.error_code == "FORBIDDEN"

    def test_list_of_trash(self, tekdrive_vcr):
        results = Trashcan(self.tekdrive).get()
        expected_trash_item_count = 8
        assert sum(1 for _ in results) == expected_trash_item_count

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
        limit = 3
        results = Trashcan(self.tekdrive).get(limit=limit)
        items = [result for result in results]
        assert len(items) <= limit

    def test_trash_get_forbidden(self, tekdrive_vcr):
        with pytest.raises(ForbiddenAPIException) as e:
            results = Trashcan(self.tekdrive).get()
            for idx, result in enumerate(results):
                pass
            assert idx == 0  # should raise on first iteration
        assert e.value.error_code == "FORBIDDEN"
