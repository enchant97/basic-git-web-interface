import pytest
from git_web.helpers import Config, get_config


@pytest.fixture(scope="session")
def app_config() -> Config:
    return get_config()
