import pickle

import pytest
from tekdrive.models import Folder
from tekdrive.exceptions import ClientException

from ...base import UnitTest


class TestFolderModel(UnitTest):
    def test_unknown_attribute(self):
        with pytest.raises(AttributeError):
            Folder(self.tekdrive, _data=dict(id="fol123")).unknown_attr

    def test_unknown_method(self):
        with pytest.raises(AttributeError):
            Folder(self.tekdrive, _data=dict(id="fol123")).unknown_method()

    def test_fetched(self):
        f1 = Folder(self.tekdrive, _data={"id": "abc123"})
        assert f1._fetched is True

        f2 = Folder(self.tekdrive, id="xyz789")
        assert f2._fetched is False

    def test_bad_init(self):
        expected_message = "An invalid value was specified for `id`."
        with pytest.raises(ValueError) as e:
            Folder(self.tekdrive)
        assert str(e.value) == expected_message

        with pytest.raises(ValueError) as e:
            Folder(self.tekdrive, id=None)
        assert str(e.value) == expected_message

        with pytest.raises(ValueError) as e:
            Folder(self.tekdrive, id="")
        assert str(e.value) == expected_message

    def test_identity(self):
        f1 = Folder(self.tekdrive, _data={"id": "abc123"})
        f2 = Folder(self.tekdrive, _data={"id": "aaaaaa"})
        assert f1 == f1
        assert f2 == f2
        assert f1 == "abc123"
        assert f2 == "aaaaaa"

    def test_equality(self):
        f1 = Folder(self.tekdrive, _data={"id": "fol123"})
        f2 = Folder(self.tekdrive, _data={"id": "fol123"})
        f3 = Folder(self.tekdrive, _data={"id": "fol999"})

        assert f1 == f2
        assert f1 != f3
        assert f2 != f3

    def test_pickle(self):
        folder = Folder(self.tekdrive, _data=dict(id="fol123"))
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(folder, protocol=level))
            assert folder == other

    def test_repr(self):
        folder = Folder(self.tekdrive, id="fol123")
        assert repr(folder) == "Folder(id='fol123')"

    def test_str(self):
        folder = Folder(self.tekdrive, id="fol123")
        assert str(folder) == "fol123"

    def test_unset_hidden_attribute_does_not_fetch(self):
        folder = Folder(self.tekdrive, _data={"id": "fol123"})
        assert folder._fetched is True
        with pytest.raises(AttributeError):
            folder._unset_hidden_attr

    def test_add_member_no_args(self):
        folder = Folder(self.tekdrive, id="fol123")
        with pytest.raises(ClientException) as e:
            folder.add_member()
        assert str(e.value) == "Must supply `username` or `user_id`."
