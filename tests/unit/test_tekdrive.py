import pytest

from tekdrive import TekDrive
from tekdrive.exceptions import ClientException, TekDriveAPIException, FileGoneAPIException

from .base import UnitTest


class TestTekDrive(UnitTest):
    FAKE_KEY = "abc123"

    def test_access_key_required(self):
        with pytest.raises(ClientException) as e:
            TekDrive(access_key=None)
        assert str(e.value).startswith("Missing required attribute 'access_key'.")

    def test_custom_base_url(self):
        base_url = "https://drive.dev-api.tekcloud.com"
        td = TekDrive(
            access_key="abc123",
            base_url=base_url,
        )
        assert td._session._request_wrapper.base_url == base_url


class TestParser(UnitTest):
    def test_parser_no_content(self):
        data = None
        assert self.tekdrive._parser.parse(data) is None

    def test_parse_error_no_error_code(self):
        for data in ({}, {"a": 1}):
            assert self.tekdrive._parser.parse_error(data, headers=None) is None

    def test_parse_error_has_error_code(self):
        data = {"errorCode": "SOME_ERROR_CODE"}
        error = self.tekdrive._parser.parse_error(data, headers=None)
        assert isinstance(error, TekDriveAPIException)

    def test_parse_file_gone(self):
        data = {"errorCode": "FILE_GONE", "message": "File is in the trash."}
        error = self.tekdrive._parser.parse_error(data, headers=None)
        assert isinstance(error, FileGoneAPIException)
