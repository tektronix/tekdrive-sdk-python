import pytest

from tekdrive.models import Folder

from ...base import IntegrationTest


@pytest.mark.integration
class TestFolder(IntegrationTest):

    def test_fetched_attributes(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        folder = Folder(self.tekdrive, id=folder_id)
        assert folder.created_at == "2021-02-08T15:56:24.003Z"
        assert folder.creator.id == "4b0dd6d7-9284-4202-b8e7-213569976c63"
        assert folder.creator.username == "thomas+tekdrive@initialstate.com"
        assert folder.folder_type == "STANDARD"
        assert folder.id == folder_id
        assert folder.name == "New Folder"
        assert folder.owner.id == "4b0dd6d7-9284-4202-b8e7-213569976c63"
        assert folder.owner.username == "thomas+tekdrive@initialstate.com"
        assert folder.permissions == {
            "creator": True,
            "edit": True,
            "owner": True,
            "public": False,
            "read": True,
        }
        assert folder.shared_at is None
        assert folder.type == "FOLDER"
        assert folder.updated_at == "2021-02-08T15:56:24.003Z"

    def test_members_only_owner(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        folder = Folder(self.tekdrive, id=folder_id)
        members = folder.members()
        assert len(members) == 1
        assert members[0] == '4b0dd6d7-9284-4202-b8e7-213569976c63'  # owner id
        assert members[0].username == "thomas+tekdrive@initialstate.com"
        assert members[0].permissions["creator"] is True
        assert members[0].permissions["edit"] is True
        assert members[0].permissions["read"] is True
        assert members[0].permissions["owner"] is True

    def test_members_multiple(self, tekdrive_vcr):
        folder_id = "eb1b996b-4eda-4068-a175-ca7135f6731b"
        folder = Folder(self.tekdrive, id=folder_id)
        members = folder.members()
        assert len(members) == 2
        for member in members:
            assert member.id is not None
            assert member.username is not None
            assert member.permissions is not None

    def test_move(self, tekdrive_vcr):
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        target_folder_id = "eb1b996b-4eda-4068-a175-ca7135f6731b"
        folder = Folder(self.tekdrive, id=folder_id)
        folder.move(target_folder_id)
        assert folder.parent_folder_id == target_folder_id
        # refresh data
        folder._fetch()
        assert folder.parent_folder_id == target_folder_id

    def test_share_defaults_to_read_only(self, tekdrive_vcr):
        sharee_username = 'thomas+3tekdrive@initialstate.com'
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        folder = Folder(self.tekdrive, id=folder_id)

        members = folder.members()
        member_count = len(members)

        sharee = folder.share(sharee_username)
        assert sharee.id is not None
        assert sharee.username == sharee_username
        assert sharee.permissions == {
            "creator": False,
            "edit": False,
            "owner": False,
            "read": True,
        }

        updated_members = folder.members()
        assert len(updated_members) == member_count + 1

    def test_share_with_edit(self, tekdrive_vcr):
        sharee_username = 'thomas+4tekdrive@initialstate.com'
        folder_id = "8e1a1ad0-d352-4681-b14e-62c7371d6043"
        folder = Folder(self.tekdrive, id=folder_id)

        members = folder.members()
        member_count = len(members)

        sharee = folder.share(sharee_username, edit_access=True)
        assert sharee.id is not None
        assert sharee.username == sharee_username
        assert sharee.permissions == {
            "creator": False,
            "edit": True,
            "owner": False,
            "read": True,
        }

        updated_members = folder.members()
        assert len(updated_members) == member_count + 1

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
