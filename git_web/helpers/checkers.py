import re
from pathlib import Path
from urllib.parse import urlparse

from .config import get_config
from .constants import RESERVED_NAMES

__all__ = [
    "is_allowed_dir", "is_valid_clone_url",
    "is_commit_hash", "is_valid_repo_name",
    "is_valid_directory_name", "is_name_reserved",
    "does_path_contain",
]


def is_allowed_dir(name: str) -> bool:
    """
    Whether given name is allowed for a directory name

        :param name: The name
        :return: Whether it is allowed
    """
    if name in get_config().DISALLOWED_DIRS:
        return False
    return True


def is_valid_clone_url(url: str) -> bool:
    """
    Whether given url is a valid clone url

        :param url: The url
        :return: Whether it is valid
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    return True


def is_commit_hash(possible_hash: str) -> bool:
    """
    Whether the given string is a valid commit hash format

        :param possible_hash: The possible hash
        :return: Whether it is valid
    """
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
    return is_valid_repo_name(name) and is_allowed_dir(name)


def is_name_reserved(name: str) -> bool:
    """
    Check whether the name is reserved,
    for use with repo name or repo directory

        :param name: name to test
        :return: whether name is reserved
    """
    return name in RESERVED_NAMES


def does_path_contain(path: Path, name: str) -> bool:
    """
    Checks whether a path contains a given name

        :param path: The path
        :param name: The name to check
        :return: Whether a match was found
    """
    return True if name in path.name else False
