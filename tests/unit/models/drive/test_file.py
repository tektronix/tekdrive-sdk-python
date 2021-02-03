import pickle

import pytest
from tekdrive.exceptions import ClientException
from tekdrive.models import File

from ...base import UnitTest


class TestFileModel(UnitTest):
    def test_unknown_attribute(self):
        with pytest.raises(AttributeError):
            File(self.tekdrive, _data=dict(id="ae80")).unknown_attr

    def test_unknown_method(self):
        with pytest.raises(AttributeError):
            File(self.tekdrive, _data=dict(id="ae80")).unknown_method()

    def test_fetched(self):
        f1 = File(self.tekdrive, _data={"id": "abc123"})
        assert f1._fetched is True

        f2 = File(self.tekdrive, id="xyz789")
        assert f2._fetched is False

    def test_bad_init(self):
        expected_message = "Must supply `id` or `_data`."
        with pytest.raises(ClientException) as e:
            File(self.tekdrive)
        assert str(e.value) == expected_message

        with pytest.raises(ClientException) as e:
            File(self.tekdrive, id=None)
        assert str(e.value) == expected_message

        with pytest.raises(ClientException) as e:
            File(self.tekdrive, id="")
        assert str(e.value) == expected_message

    def test_identity(self):
        f1 = File(self.tekdrive, _data={"id": "abc123"})
        f2 = File(self.tekdrive, _data={"id": "aaaaaa"})
        assert f1 == f1
        assert f2 == f2
        assert f1 == 'abc123'
        assert f2 == 'aaaaaa'

    def test_equality(self):
        f1 = File(self.tekdrive, _data={"id": "ae80"})
        f2 = File(self.tekdrive, _data={"id": "ae80"})
        f3 = File(self.tekdrive, _data={"id": "cc12"})

        assert f1 == f2
        assert f1 != f3
        assert f2 != f3

    def test_pickle(self):
        file = File(self.tekdrive, _data=dict(id="ae80"))
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(file, protocol=level))
            assert file == other

    def test_repr(self):
        file = File(self.tekdrive, id="ae80")
        assert repr(file) == "File(id='ae80')"

    def test_str(self):
        file = File(self.tekdrive, id="ae80")
        assert str(file) == "ae80"

    def test_unset_hidden_attribute_does_not_fetch(self):
        file = File(self.tekdrive, _data={"id": "ae80"})
        assert file._fetched is True
        with pytest.raises(AttributeError):
            file._unset_hidden_attr
