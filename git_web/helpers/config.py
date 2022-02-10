from functools import cache
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings

__all__ = [
    "Config", "get_config",
]


class Config(BaseSettings):
    """
    the app config format
    """
    REPOS_PATH: Path
    REPOS_SSH_BASE: str
    LOGIN_PASSWORD: str
    SECRET_KEY: str
    DEFAULT_BRANCH: Optional[str] = "main"
    DISALLOWED_DIRS: Optional[list[str]] = []
    MAX_COMMIT_LOG_COUNT: Optional[int] = 20
    SSH_PUB_KEY_PATH: Optional[Path] = None
    SSH_AUTH_KEYS_PATH: Optional[Path] = None
    HTTP_GIT_ENABLED: Optional[bool] = True

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


@cache
def get_config() -> Config:  # pragma: no cover
    """
    get the app config from environment variables.
    will exit(1) if error occurs

        :return: the app config
    """
    return Config()
