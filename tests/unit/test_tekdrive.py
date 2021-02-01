import pytest
from unittest import mock

from tekdrive import TekDrive
from tekdrive.core import Requestor
from tekdrive.exceptions import ClientException, TekDriveAPIException

from .base import UnitTest


class TestTekDrive(UnitTest):
    FAKE_KEY = "abc123"

    def test_access_key_required(self):
        with pytest.raises(ClientException) as excinfo:
            TekDrive(access_key=None)
        assert str(excinfo.value).startswith(
            "Missing required attribute 'access_key'."
        )

    def test_custom_requestor_class(self):
        class CustomRequestor(Requestor):
            pass

        td = TekDrive(
            access_key="abc123",
            requestor_class=CustomRequestor,
        )
        assert isinstance(td._core._requestor, CustomRequestor)
        assert not isinstance(self.tekdrive._core._requestor, CustomRequestor)

    def test_custom_requestor_kwargs(self):
        session = mock.Mock(headers={})
        base_url = "https://drive.dev-api.tekcloud.com"
        td = TekDrive(
            access_key="abc123",
            requestor_kwargs={
                "base_url": base_url,
                "session": session
            },
        )

        assert td._core._requestor._http is session
        assert td._core._requestor.base_url == base_url


class TestParser(UnitTest):
    def test_parser_no_content(self):
        data = None
        assert self.tekdrive._parser.parse(data) is None

    def test_parse_error_no_error_code(self):
        for data in ({}, {"a": 1}):
            assert self.tekdrive._parser.parse_error(data) is None

    def test_parse_error_has_error_code(self):
        data = {
            "errorCode": "SOME_ERROR_CODE"
        }
        error = self.tekdrive._parser.parse_error(data)
        assert isinstance(error, TekDriveAPIException)
