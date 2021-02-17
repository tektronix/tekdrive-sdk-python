import pytest
from datetime import datetime

# from tekdrive.exceptions import ClientException, TekDriveAPIException
from tekdrive.models import File

from ...base import IntegrationTest


@pytest.mark.integration
class TestFile(IntegrationTest):

    def test_fetched_attributes(self, tekdrive_vcr):
        file_id = "7682b062-aeaf-4b29-997e-d9178db05d5f"
        file = File(self.tekdrive, id=file_id)
        assert file.bytes == "14"
        assert file.created_at == datetime.strptime("2021-02-02T20:40:17.533Z", "%Y-%m-%dT%H:%M:%S.%fZ")
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
        assert file.updated_at == datetime.strptime("2021-02-02T20:40:18.884Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        assert file.upload_state == "SUCCESS"

    def test_members_only_owner(self, tekdrive_vcr):
        file_id = "3670359c-c453-40b7-bcc1-0281e2f6db94"
        file = File(self.tekdrive, id=file_id)
        members = file.members()
        assert len(members) == 1
        assert members[0] == '4b0dd6d7-9284-4202-b8e7-213569976c63'  # owner id
        assert members[0].username == "thomas+tekdrive@initialstate.com"
        assert members[0].permissions["creator"] is True
        assert members[0].permissions["edit"] is True
        assert members[0].permissions["read"] is True
        assert members[0].permissions["owner"] is True

    def test_members_multiple(self, tekdrive_vcr):
        file_id = "3670359c-c453-40b7-bcc1-0281e2f6db94"
        file = File(self.tekdrive, id=file_id)
        members = file.members()
        assert len(members) == 2
        for member in members:
            assert member.id is not None
            assert member.username is not None
            assert member.permissions is not None

    def test_move(self, tekdrive_vcr):
        file_id = "3670359c-c453-40b7-bcc1-0281e2f6db94"
        target_folder_id = "b0c9dbce-fe01-4f05-8a0d-5e7041c04e6a"
        file = File(self.tekdrive, id=file_id)
        file.move(target_folder_id)
        assert file.parent_folder_id == target_folder_id
        # refresh data
        file._fetch()
        assert file.parent_folder_id == target_folder_id

    def test_share_defaults_to_read_only(self, tekdrive_vcr):
        sharee_username = 'thomas+3tekdrive@initialstate.com'
        file_id = "e5e4b89b-0043-47ec-a982-439081361ed9"
        file = File(self.tekdrive, id=file_id)

        members = file.members()
        member_count = len(members)

        sharee = file.share(sharee_username)
        assert sharee.id is not None
        assert sharee.username == sharee_username
        assert sharee.permissions == {
            "creator": False,
            "edit": False,
            "owner": False,
            "read": True,
        }

        updated_members = file.members()
        assert len(updated_members) == member_count + 1

    def test_share_with_edit(self, tekdrive_vcr):
        sharee_username = 'thomas+3tekdrive@initialstate.com'
        file_id = "7fa7559a-5339-4ec2-8e57-392857d96706"
        file = File(self.tekdrive, id=file_id)

        members = file.members()
        member_count = len(members)

        sharee = file.share(sharee_username, edit_access=True)
        assert sharee.id is not None
        assert sharee.username == sharee_username
        assert sharee.permissions == {
            "creator": False,
            "edit": True,
            "owner": False,
            "read": True,
        }

        updated_members = file.members()
        assert len(updated_members) == member_count + 1

    def test_update_name(self, tekdrive_vcr):
        file_id = "3670359c-c453-40b7-bcc1-0281e2f6db94"
        old_name = "old_name"
        new_name = "my_new_name"
        file = File(self.tekdrive, id=file_id)
        assert file.name == old_name

        file.name = new_name
        file.save()

        # refresh data
        file._fetch()
        assert file.name == new_name
