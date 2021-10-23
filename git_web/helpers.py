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


def find_repos(repo_dir: Path, make_relative: bool = False):
    """
    Find git bare repos (.git) in given directory,
    will not recurse.

        :param repo_dir: Directory to search in
        :param make_relative: Whether to make path relative, defaults to False
        :yield: The found repo
    """
    found = repo_dir.glob("*.git")
    if make_relative:
        for path in found:
            yield Path(path).relative_to(repo_dir)
    else:
        for path in found:
            yield Path(path)


def combine_full_dir(repo_dir: str) -> Path:
    return get_config().REPOS_PATH / repo_dir


def combine_full_dir_repo(repo_dir: str, repo_name: str) -> Path:
    return get_config().REPOS_PATH / repo_dir / (repo_name + ".git")


def find_dirs() -> filter:
    return filter(
        is_allowed_dir,
        next(os.walk(get_config().REPOS_PATH))[1]
    )


def create_ssh_uri(repo_path: Path) -> str:
    return get_config().REPOS_SSH_BASE + ":" +\
         str(repo_path.relative_to(get_config().REPOS_PATH))
