import os
import sys

import pytest

# print(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# print(sys.path)

from snakeeyes.app import create_app


@pytest.fixture(scope="session")
def app():
    """
    Setup our flask test app, this only gets executed once.

    :return: Flask app
    """
    params = {
        "DEBUG": False,
        "TESTING": True,
    }

    _app = create_app(settings_override=params)

    # Establish an application context before running the tests
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="function")
def client(app):
    """
    Setup an app client, this gets executed for each test function.

    :param app: Pytest fixture
    :return: Flask app client
    """
    print(type(app))
    yield app.test_client()
