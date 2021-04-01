import pytest
from datetime import datetime

from tekdrive.exceptions import TekDriveAPIException
from tekdrive.models import File, Permissions
from tekdrive.enums import ObjectType

from ...base import IntegrationTest


@pytest.mark.integration
class TestFile(IntegrationTest):
    def test_fetched_attributes(self, tekdrive_vcr):
        file_id = "7682b062-aeaf-4b29-997e-d9178db05d5f"
        file = File(self.tekdrive, id=file_id)
        assert file.bytes == "14"
        assert file.created_at == datetime.strptime(
            "2021-02-02T20:40:17.533Z", "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        assert file.creator.id == "4b0dd6d7-9284-4202-b8e7-213569976c63"
        assert file.creator.username == "thomas+tekdrive@initialstate.com"
        assert file.file_type == "TXT"
        assert file.id == file_id
        assert file.name == "test_file.txt"
        assert file.owner.id == "4b0dd6d7-9284-4202-b8e7-213569976c63"
        assert file.owner.username == "thomas+tekdrive@initialstate.com"
        assert file.permissions == Permissions(
            creator=True,
            edit=True,
            owner=True,
            public=False,
            read=True,
        )
        assert file.shared_at is None
        assert file.type == ObjectType.FILE
        assert file.updated_at == datetime.strptime(
            "2021-02-02T20:40:18.884Z", "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        assert file.upload_state == "SUCCESS"

    def test_members_only_owner(self, tekdrive_vcr):
        file_id = "3670359c-c453-40b7-bcc1-0281e2f6db94"
        file = File(self.tekdrive, id=file_id)
        members = file.members()
        assert len(members) == 1
        assert members[0] == "4b0dd6d7-9284-4202-b8e7-213569976c63"  # owner id
        assert members[0].username == "thomas+tekdrive@initialstate.com"
        assert members[0].permissions.creator is True
        assert members[0].permissions.edit is True
        assert members[0].permissions.read is True
        assert members[0].permissions.owner is True

    def test_members_multiple(self, tekdrive_vcr):
        file_id = "3670359c-c453-40b7-bcc1-0281e2f6db94"
        file = File(self.tekdrive, id=file_id)
        members = file.members()
        assert len(members) == 2
        for member in members:
            assert member.id is not None
            assert member.username is not None
            assert isinstance(member.permissions, Permissions)
            assert member.permissions.read is True  # should at least have read

    def test_move(self, tekdrive_vcr):
        file_id = "3670359c-c453-40b7-bcc1-0281e2f6db94"
        target_folder_id = "b0c9dbce-fe01-4f05-8a0d-5e7041c04e6a"
        file = File(self.tekdrive, id=file_id)
        file.move(target_folder_id)
        assert file.parent_folder_id == target_folder_id
        # refresh data
        file._fetch()
        assert file.parent_folder_id == target_folder_id

    def test_add_member_defaults_to_read_only(self, tekdrive_vcr):
        sharee_username = "thomas+3tekdrive@initialstate.com"
        file_id = "e5e4b89b-0043-47ec-a982-439081361ed9"
        file = File(self.tekdrive, id=file_id)

        members = file.members()
        member_count = len(members)

        sharee = file.add_member(sharee_username)
        assert sharee.id is not None
        assert sharee.username == sharee_username
        assert sharee.permissions == Permissions(
            creator=False,
            edit=False,
            owner=False,
            read=True,
        )

        updated_members = file.members()
        assert len(updated_members) == member_count + 1

    def test_add_member_with_edit(self, tekdrive_vcr):
        sharee_username = "thomas+3tekdrive@initialstate.com"
        file_id = "7fa7559a-5339-4ec2-8e57-392857d96706"
        file = File(self.tekdrive, id=file_id)

        members = file.members()
        member_count = len(members)

        sharee = file.add_member(sharee_username, edit_access=True)
        assert sharee.id is not None
        assert sharee.username == sharee_username
        assert sharee.permissions == Permissions(
            creator=False,
            edit=True,
            owner=False,
            read=True,
        )

        updated_members = file.members()
        assert len(updated_members) == member_count + 1

    def test_add_member_by_id(self, tekdrive_vcr):
        file_id = "7fa7559a-5339-4ec2-8e57-392857d96706"
        sharee_id = "67833b18-6941-4728-b326-0e5973b32e75"
        file = File(self.tekdrive, id=file_id)

        members = file.members()
        member_count = len(members)

        sharee = file.add_member(user_id=sharee_id, edit_access=True)
        assert sharee.id is not None
        assert sharee.username == "thomas+2tekdrive@initialstate.com"
        assert sharee.permissions == Permissions(
            creator=False,
            edit=True,
            owner=False,
            read=True,
        )

        updated_members = file.members()
        assert len(updated_members) == member_count + 1

    def test_add_member_by_id_which_dne(self, tekdrive_vcr):
        file_id = "7fa7559a-5339-4ec2-8e57-392857d96706"
        made_up_user_id = "4307a1f5-edc1-4082-8bb2-05068d6c1d67"
        file = File(self.tekdrive, id=file_id)

        with pytest.raises(TekDriveAPIException) as e:
            file.add_member(user_id=made_up_user_id, edit_access=True)
        assert e.value.error_code == "UNPROCESSABLE_ENTITY"
        assert e.value.request_id == "b185d388-3b93-45c4-a61a-fc7591630038"

    def test_remove_member_by_id(self, tekdrive_vcr):
        file_id = "7fa7559a-5339-4ec2-8e57-392857d96706"
        member_id = "67833b18-6941-4728-b326-0e5973b32e75"
        file = File(self.tekdrive, id=file_id)

        members = file.members()
        member_count = len(members)
        assert member_id in [member.id for member in members]

        file.remove_member(user_id=member_id)

        updated_members = file.members()
        assert len(updated_members) == member_count - 1
        assert member_id not in [member.id for member in updated_members]

    def test_remove_member_by_id_which_dne(self, tekdrive_vcr):
        file_id = "fcfba73d-4ef7-408e-bb74-a2b45d5a947a"
        made_up_user_id = "4307a1f5-edc1-4082-8bb2-05068d6c1d67"
        file = File(self.tekdrive, id=file_id)

        member_ids_before = [member.id for member in file.members()]

        # expect nothing to change
        file.remove_member(user_id=made_up_user_id)

        member_ids_after = [member.id for member in file.members()]

        assert sorted(member_ids_before) == sorted(member_ids_after)

    def test_remove_member_owner(self, tekdrive_vcr):
        file_id = "fcfba73d-4ef7-408e-bb74-a2b45d5a947a"
        owner_user_id = "4b0dd6d7-9284-4202-b8e7-213569976c63"
        file = File(self.tekdrive, id=file_id)

        with pytest.raises(TekDriveAPIException) as e:
            file.remove_member(user_id=owner_user_id)
        assert e.value.error_code == "FORBIDDEN"
        assert e.value.message == "Cannot remove owner"
        assert e.value.request_id == "82efe8d8-77e7-4f30-b1a2-069bc0f86052"

    def test_modify_member_revoke_edit(self, tekdrive_vcr):
        file_id = "fcfba73d-4ef7-408e-bb74-a2b45d5a947a"
        user_id = "7869c0bf-ad79-4e44-a374-ec87294bab9e"
        file = File(self.tekdrive, id=file_id)

        updated_member = file.modify_member(user_id=user_id, edit_access=False)
        assert updated_member.permissions.edit is False

    def test_modify_member_cannot_revoke_owner_edit(self, tekdrive_vcr):
        file_id = "fcfba73d-4ef7-408e-bb74-a2b45d5a947a"
        owner_user_id = "4b0dd6d7-9284-4202-b8e7-213569976c63"
        file = File(self.tekdrive, id=file_id)

        with pytest.raises(TekDriveAPIException) as e:
            file.modify_member(user_id=owner_user_id, edit_access=False)
        assert e.value.error_code == "FORBIDDEN"
        assert e.value.message == "Cannot update owner"
        assert e.value.request_id == "ff96ab2e-e0c8-4b65-9a7c-4dd92343d95f"

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

    def test_delete_default(self, tekdrive_vcr):
        file_id = "05e340ea-eb6d-4c01-aa7e-6752d2e00111"
        file = File(self.tekdrive, id=file_id)
        file.delete()

        with pytest.raises(TekDriveAPIException) as e:
            file._fetch()
        assert e.value.error_code == "FILE_GONE"

    def test_delete_hard_delete(self, tekdrive_vcr):
        file_id = "6aaaced0-1884-41e2-a4d9-36e0e0f6f1d7"
        file = File(self.tekdrive, id=file_id)
        file.delete(hard_delete=True)

        with pytest.raises(TekDriveAPIException) as e:
            file._fetch()
        assert e.value.error_code == "FILE_NOT_FOUND"

    def test_delete_not_found(self, tekdrive_vcr):
        file_id = "457b7075-555c-4031-95b1-2a55c33b20dc"
        file = File(self.tekdrive, id=file_id)
        with pytest.raises(TekDriveAPIException) as e:
            file.delete()
        assert e.value.error_code == "FILE_NOT_FOUND"

    def test_delete_forbidden(self, tekdrive_vcr):
        file_id = "d11758f8-5644-4078-8f02-7168104208dd"
        file = File(self.tekdrive, id=file_id)
        with pytest.raises(TekDriveAPIException) as e:
            file.delete()
        assert e.value.error_code == "FORBIDDEN"
