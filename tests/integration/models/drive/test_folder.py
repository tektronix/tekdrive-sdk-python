import pytest
from datetime import datetime

from tekdrive.models import Folder, Permissions
from tekdrive.exceptions import TekDriveAPIException
from tekdrive.enums import ObjectType

from ...base import IntegrationTest


@pytest.mark.integration
class TestFolder(IntegrationTest):
    def test_fetched_attributes(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        folder = Folder(self.tekdrive, id=folder_id)
        assert folder.created_at == datetime.strptime(
            "2021-02-08T15:56:24.003Z", "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        assert folder.creator.id == "4b0dd6d7-9284-4202-b8e7-213569976c63"
        assert folder.creator.username == "thomas+tekdrive@initialstate.com"
        assert folder.folder_type == "STANDARD"
        assert folder.id == folder_id
        assert folder.name == "New Folder"
        assert folder.owner.id == "4b0dd6d7-9284-4202-b8e7-213569976c63"
        assert folder.owner.username == "thomas+tekdrive@initialstate.com"
        assert folder.permissions == Permissions(
            creator=True,
            edit=True,
            owner=True,
            public=False,
            read=True,
        )
        assert folder.shared_at is None
        assert folder.type == ObjectType.FOLDER
        assert folder.updated_at == datetime.strptime(
            "2021-02-08T15:56:24.003Z", "%Y-%m-%dT%H:%M:%S.%fZ"
        )

    def test_members_only_owner(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        folder = Folder(self.tekdrive, id=folder_id)
        members = folder.members()
        assert len(members) == 1
        assert members[0] == "4b0dd6d7-9284-4202-b8e7-213569976c63"  # owner id
        assert members[0].username == "thomas+tekdrive@initialstate.com"
        assert members[0].permissions.creator is True
        assert members[0].permissions.edit is True
        assert members[0].permissions.read is True
        assert members[0].permissions.owner is True

    def test_members_multiple(self, tekdrive_vcr):
        folder_id = "eb1b996b-4eda-4068-a175-ca7135f6731b"
        folder = Folder(self.tekdrive, id=folder_id)
        members = folder.members()
        assert len(members) == 2
        for member in members:
            assert member.id is not None
            assert member.username is not None
            assert isinstance(member.permissions, Permissions)
            assert member.permissions.read is True  # should at least have read

    def test_move(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        target_folder_id = "eb1b996b-4eda-4068-a175-ca7135f6731b"
        folder = Folder(self.tekdrive, id=folder_id)
        folder.move(target_folder_id)
        assert folder.parent_folder_id == target_folder_id
        # refresh data
        folder._fetch()
        assert folder.parent_folder_id == target_folder_id

    def test_add_member_defaults_to_read_only(self, tekdrive_vcr):
        sharee_username = "thomas+3tekdrive@initialstate.com"
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        folder = Folder(self.tekdrive, id=folder_id)

        members = folder.members()
        member_count = len(members)

        sharee = folder.add_member(sharee_username)
        assert sharee.id is not None
        assert sharee.username == sharee_username
        assert sharee.permissions == Permissions(
            creator=False,
            edit=False,
            owner=False,
            read=True,
        )

        updated_members = folder.members()
        assert len(updated_members) == member_count + 1

    def test_add_member_with_edit(self, tekdrive_vcr):
        sharee_username = "thomas+4tekdrive@initialstate.com"
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        folder = Folder(self.tekdrive, id=folder_id)

        members = folder.members()
        member_count = len(members)

        sharee = folder.add_member(sharee_username, edit_access=True)
        assert sharee.id is not None
        assert sharee.username == sharee_username
        assert sharee.permissions == Permissions(
            creator=False,
            edit=True,
            owner=False,
            read=True,
        )

        updated_members = folder.members()
        assert len(updated_members) == member_count + 1

    def test_add_member_by_id(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        sharee_id = "67833b18-6941-4728-b326-0e5973b32e75"
        folder = Folder(self.tekdrive, id=folder_id)

        members = folder.members()
        member_count = len(members)

        sharee = folder.add_member(user_id=sharee_id, edit_access=True)
        assert sharee.id is not None
        assert sharee.username == "thomas+2tekdrive@initialstate.com"
        assert sharee.permissions == Permissions(
            creator=False,
            edit=True,
            owner=False,
            read=True,
        )

        updated_members = folder.members()
        assert len(updated_members) == member_count + 1

    def test_add_member_by_id_which_dne(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        made_up_user_id = "4307a1f5-edc1-4082-8bb2-05068d6c1d67"
        folder = Folder(self.tekdrive, id=folder_id)

        with pytest.raises(TekDriveAPIException) as e:
            folder.add_member(user_id=made_up_user_id, edit_access=True)
        assert e.value.error_code == "UNPROCESSABLE_ENTITY"

    def test_remove_member_by_id(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        member_id = "67833b18-6941-4728-b326-0e5973b32e75"
        folder = Folder(self.tekdrive, id=folder_id)

        members = folder.members()
        member_count = len(members)
        assert member_id in [member.id for member in members]

        folder.remove_member(user_id=member_id)

        updated_members = folder.members()
        assert len(updated_members) == member_count - 1
        assert member_id not in [member.id for member in updated_members]

    def test_remove_member_by_id_which_dne(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        made_up_user_id = "4307a1f5-edc1-4082-8bb2-05068d6c1d67"
        folder = Folder(self.tekdrive, id=folder_id)

        member_ids_before = [member.id for member in folder.members()]

        # expect nothing to change
        folder.remove_member(user_id=made_up_user_id)

        member_ids_after = [member.id for member in folder.members()]

        assert sorted(member_ids_before) == sorted(member_ids_after)

    def test_remove_member_owner(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        owner_user_id = "4b0dd6d7-9284-4202-b8e7-213569976c63"
        folder = Folder(self.tekdrive, id=folder_id)

        with pytest.raises(TekDriveAPIException) as e:
            folder.remove_member(user_id=owner_user_id)
        assert e.value.error_code == "FORBIDDEN"
        assert e.value.message == "Cannot remove owner"

    def test_modify_member_revoke_edit(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        user_id = "7869c0bf-ad79-4e44-a374-ec87294bab9e"
        folder = Folder(self.tekdrive, id=folder_id)

        updated_member = folder.modify_member(user_id=user_id, edit_access=False)
        assert updated_member.permissions.edit is False

    def test_modify_member_cannot_revoke_owner_edit(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        owner_user_id = "4b0dd6d7-9284-4202-b8e7-213569976c63"
        folder = Folder(self.tekdrive, id=folder_id)

        with pytest.raises(TekDriveAPIException) as e:
            folder.modify_member(user_id=owner_user_id, edit_access=False)
        assert e.value.error_code == "FORBIDDEN"
        assert e.value.message == "Cannot update owner"

    def test_update_name(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        old_name = "New Folder"
        new_name = "my_new_name"
        folder = Folder(self.tekdrive, id=folder_id)
        assert folder.name == old_name

        folder.name = new_name
        folder.save()

        # refresh data
        folder._fetch()
        assert folder.name == new_name
