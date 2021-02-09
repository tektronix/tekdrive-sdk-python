import pytest
from tekdrive.exceptions import ClientException
from tekdrive.models import Search

from ..base import UnitTest


class TestSearchModel(UnitTest):
    def test_name_required(self):
        with pytest.raises(ClientException) as e:
            Search(self.tekdrive).query()
        assert str(e.value).startswith(
            "Must supply `name`, `file_type`, or `upload_state`."
        )

        with pytest.raises(ClientException) as e:
            Search(self.tekdrive).query(name=None)
        assert str(e.value).startswith(
            "Must supply `name`, `file_type`, or `upload_state`."
        )
