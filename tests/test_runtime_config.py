import os

import pytest

os.environ["OTHCTL_MACHINE"] = "minimal_machine"

from oth.config import get_from_environ

# ---------------------------------------------------------------------------
# Test get_from_environ
# ---------------------------------------------------------------------------


def test_get_from_environ(monkeypatch):
    assert get_from_environ("TEST_ENVVAR") == None
    assert get_from_environ("TEST_ENVVAR", default="pytest") == "pytest"

    try:
        get_from_environ("TEST_ENVVAR", required=True)
        pytest.fail(
            "get_from_environ did not raise an exception when given a non-existent environment variable and required=True"
        )
    except ValueError:
        pass

    with monkeypatch.context() as mp:
        mp.setenv("TEST_ENVVAR", "pytest")
        assert get_from_environ("TEST_ENVVAR") == "pytest"
