import pytest
from datetime import datetime

from tekdrive.models import DriveUser, User, Plan, Usage
from tekdrive.enums import SharingType

from ..base import IntegrationTest


@pytest.mark.integration
class TestSearch(IntegrationTest):
    def test_me_user_info(self, tekdrive_vcr):
        me = User(self.tekdrive).me()
        assert isinstance(me, DriveUser)
        assert me.id == "4b0dd6d7-9284-4202-b8e7-213569976c63"
        assert me.username == "thomas+tekdrive@initialstate.com"
        assert me.account_id == "act_2s9zm7keogrmij"
        assert me.created_at == datetime.strptime(
            "2020-09-04T16:39:47.369Z", "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        assert me.updated_at == datetime.strptime(
            "2020-09-04T16:39:55.079Z", "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        assert me.owner_type == "USER"

    def test_me_plan_info(self, tekdrive_vcr):
        me = User(self.tekdrive).me()
        plan = me.plan
        assert isinstance(plan, Plan)
        assert plan.id == "pln_testsmall"
        assert plan.name == "Test Small Limits"
        assert plan.access_key_limit == 20
        assert plan.storage_limit == 2e9
        assert plan.sharing_type == SharingType.UNLIMITED

    def test_usage(self, tekdrive_vcr):
        usage = User(self.tekdrive).usage()
        assert isinstance(usage, Usage)
        assert usage.files_created_count == 70
        assert usage.files_owned_count == 70
        assert usage.files_owned_in_trash_count == 0
        assert usage.storage_freeable == 0
        assert usage.storage_limit == 2e9
        assert usage.storage_remaining == 969146060
        assert usage.storage_used == 1030853940
