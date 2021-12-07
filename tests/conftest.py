import pytest
from git_web.helpers import Config, get_config
from git_web.main import create_app
from quart.app import Quart


@pytest.fixture(scope="session")
def app_config() -> Config:
    return get_config()


@pytest.fixture(scope="session")
@pytest.mark.usefixtures("app")
def app() -> Quart:
    return create_app()
