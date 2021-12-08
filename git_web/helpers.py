import os
import re
import stat
import sys
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from git_interface.datatypes import TreeContent, TreeContentTypes


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
    return combine_full_dir(repo_dir) / (repo_name + ".git")


def find_dirs() -> filter:
    return filter(
        is_allowed_dir,
        next(os.walk(get_config().REPOS_PATH))[1]
    )


def sort_repo_tree(repo_tree: Iterable[TreeContent]) -> tuple[TreeContent]:
    """
    sorts a repository tree into order, folders a-z then files a-z

        :param repo_tree: the repository tree
        :return: sorted tree
    """
    trees = []
    blobs = []

    for obj in repo_tree:
        if obj.type_ == TreeContentTypes.BLOB:
            blobs.append(obj)
        else:
            trees.append(obj)

    trees.sort(key=lambda x: x.file)
    blobs.sort(key=lambda x: x.file)

    trees.extend(blobs)
    return tuple(trees)


def create_ssh_uri(repo_path: Path) -> str:
    return get_config().REPOS_SSH_BASE + ":" +\
        str(repo_path.relative_to(get_config().REPOS_PATH)).replace("\\", "/")


def is_valid_clone_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    return True


def pathlib_delete_ro_file(action, name, exc):  # pragma: no cover
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


def is_commit_hash(possible_hash: str) -> bool:
    return True if re.match(r"^[a-zA-Z0-9]+$", possible_hash) else False


def is_valid_repo_name(name: str) -> bool:
    """
    Checks whether given name can be a valid repository name

        :param name: the name to check
        :return: whether given name is valid
    """
    return True if re.match(r"^[a-zA-Z0-9-_]+$", name) and len(name) <= 100 else False


def is_valid_directory_name(name: str) -> bool:
    """
    Checks whether given name can be a valid directory name

        :param name: the name to check
        :return: whether given name is valid
    """
    return is_valid_repo_name(name)


def safe_combine_full_dir(repo_dir: str) -> Path:
    """
    Create fullpath from a directory name,
    will make sure given data is valid

        :param repo_dir: A repository directory
        :raises ValueError: If directory name is invalid
        :return: The combined path
    """
    if not is_valid_directory_name(repo_dir):
        raise ValueError("'repo_dir' not valid")
    return combine_full_dir(repo_dir)


def safe_combine_full_dir_repo(repo_dir: str, repo_name: str) -> Path:
    """
    Combine a directory name and a repository name together,
    will make sure given data is valid

        :param repo_dir: A repository directory
        :param repo_name: A repository name, exlcuding any file extensions
        :raises ValueError: If directory name is invalid
        :raises ValueError: If repo name is invalid
        :return: The combined path
    """
    if not is_valid_directory_name(repo_dir):
        raise ValueError("'repo_dir' not valid")
    if not is_valid_repo_name(repo_name):
        raise ValueError("'repo_name' not valid")
    return combine_full_dir_repo(repo_dir, repo_name)
