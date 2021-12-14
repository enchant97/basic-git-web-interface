import os
import sys
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Optional

__all__ = [
    "Config", "get_config",
]


@dataclass
class Config:
    """
    the app config format
    """
    REPOS_PATH: Path
    REPOS_SSH_BASE: str
    LOGIN_PASSWORD: str
    SECRET_KEY: str
    DISALLOWED_DIRS: list[str]
    DEFAULT_BRANCH: str
    MAX_COMMIT_LOG_COUNT: int
    SSH_PUB_KEY_PATH: Optional[Path] = None
    SSH_AUTH_KEYS_PATH: Optional[Path] = None


@cache
def get_config() -> Config:  # pragma: no cover
    """
    get the app config from environment variables.
    will exit(1) if error occurs

        :return: the app config
    """
    try:
        return Config(
            REPOS_PATH=Path(os.environ["REPOS_PATH"]),
            REPOS_SSH_BASE=os.environ["REPOS_SSH_BASE"],
            LOGIN_PASSWORD=os.environ["LOGIN_PASSWORD"],
            SECRET_KEY=os.environ["SECRET_KEY"],
            DISALLOWED_DIRS=os.environ.get("DISALLOWED_DIRS", "").split(","),
            DEFAULT_BRANCH=os.environ.get("DEFAULT_BRANCH", "main"),
            MAX_COMMIT_LOG_COUNT=os.environ.get("MAX_COMMIT_LOG_COUNT", 20),
            SSH_PUB_KEY_PATH=os.environ.get("SSH_PUB_KEY_PATH", None),
            SSH_AUTH_KEYS_PATH=os.environ.get("SSH_AUTH_KEYS_PATH", None),
        )
    except KeyError:
        print("missing required configs", file=sys.stderr)
        exit(1)
    except ValueError:
        print("config in wrong format", file=sys.stderr)
        exit(1)
