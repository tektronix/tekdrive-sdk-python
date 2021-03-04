import logging

from tekdrive import TekDrive


class IntegrationTest:
    """Base class for integration tests."""

    logger = logging.getLogger(__name__)

    def setup(self):
        self.setup_tekdrive()

    def setup_tekdrive(self):
        self.tekdrive = TekDrive(access_key="<TEST_ACCESS_KEY>")
