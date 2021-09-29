import os
import sys
from dataclasses import dataclass
from functools import cache
from pathlib import Path


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


@cache
def get_config() -> Config:
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
        )
    except KeyError:
        print("missing required configs", file=sys.stderr)
        exit(1)
    except ValueError:
        print("config in wrong format", file=sys.stderr)
        exit(1)


def is_allowed_dir(name: str) -> bool:
    if name in get_config().DISALLOWED_DIRS:
        return False
    return True
