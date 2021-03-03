from tekdrive import TekDrive


class UnitTest:
    """Base class for unit tests."""

    def setup(self):
        self.tekdrive = TekDrive(access_key="abc123")

        # prevent unit test from making HTTP request
        self.tekdrive._core._requestor._http = None
