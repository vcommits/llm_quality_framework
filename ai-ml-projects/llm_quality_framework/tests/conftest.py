# File: tests/conftest.py
# Purpose: This special pytest file is used to define project-wide fixtures
# and custom command-line options for your test suite.

import pytest

def pytest_addoption(parser):
    """
    This function is a special hook that pytest uses to add custom command-line options.
    We are adding a '--live-api' flag.
    """
    parser.addoption(
        "--live-api", action="store_true", default=False, help="Run tests against the live APIs instead of mock mode."
    )

@pytest.fixture
def live_api_mode(request):
    """
    This is a pytest 'fixture'. It reads the value of the command-line option
    we just created and provides it to any test function that asks for it.
    """
    return request.config.getoption("--live-api")
