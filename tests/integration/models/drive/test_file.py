import pytest

# from tekdrive.exceptions import ClientException, TekDriveAPIException
from tekdrive.models import File

from ...base import IntegrationTest


@pytest.mark.integration
class TestFile(IntegrationTest):

    def test_fetched_attributes(self, tekdrive_vcr):
        file_id = "7682b062-aeaf-4b29-997e-d9178db05d5f"
        file = File(self.tekdrive, id=file_id)
        assert file.bytes == "14"
        assert file.created_at == "2021-02-02T20:40:17.533Z"
        assert file.creator.id == "4b0dd6d7-9284-4202-b8e7-213569976c63"
        assert file.creator.username == "thomas+tekdrive@initialstate.com"
        assert file.file_type == "TXT"
        assert file.id == file_id
        assert file.name == "test_file.txt"
        assert file.owner.id == "4b0dd6d7-9284-4202-b8e7-213569976c63"
        assert file.owner.username == "thomas+tekdrive@initialstate.com"
        assert file.permissions == {
            "creator": True,
            "edit": True,
            "owner": True,
            "public": False,
            "read": True,
        }
        assert file.shared_at is None
        assert file.type == "FILE"
        assert file.updated_at == "2021-02-02T20:40:18.884Z"
        assert file.upload_state == "SUCCESS"
