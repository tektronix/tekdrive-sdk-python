import time
from pathlib import Path

import pytest
import vcr


# Prevent calls to sleep
def _sleep(*args):
    raise Exception("Call to sleep")


time.sleep = _sleep


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest file after
    the command line options have been parsed.
    """
    pass


def pytest_itemcollected(item):
    """
    Any logic to run during test collection step.
    """
    if "tekdrive_vcr" in item.fixturenames:
        # Tests with tekdrive_vcr fixtures are automatically 'integration' tests
        item.add_marker("integration")


@pytest.fixture
def tekdrive_vcr(request):
    current_path = Path(request.node.fspath)
    current_path_name = current_path.name.replace(".py", "")
    cls_name = request.node.cls.__name__
    cassete_path = current_path.parent / "cassetes" / current_path_name / cls_name
    current_name = request.node.name
    casset_file_path = str(cassete_path / f"{current_name}.yaml")
    with vcr.use_cassette(
        casset_file_path,
        record_mode="once",
        filter_headers=[("x-is-ak", "TEST_ACCESS_KEY")],
        match_on=["method", "scheme", "host", "port", "path"],
    ) as cassete_maker:
        yield cassete_maker
