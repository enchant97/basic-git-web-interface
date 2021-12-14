import os
import stat
from pathlib import Path
from typing import Generator, Iterable, Iterator

from git_interface.datatypes import TreeContent, TreeContentTypes

from .checkers import (is_allowed_dir, is_valid_directory_name,
                       is_valid_repo_name)
from .config import get_config
from .types import PathComponent

__all__ = [
    "find_repos", "combine_full_dir",
    "combine_full_dir_repo", "find_dirs",
    "sort_repo_tree", "create_ssh_uri",
    "pathlib_delete_ro_file", "safe_combine_full_dir",
    "safe_combine_full_dir_repo", "path_to_tree_components",
]


def find_repos(repo_dir: Path, make_relative: bool = False) -> Generator[None, None, Path]:
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
    """
    Combine a repo directory name into a system path

        :param repo_dir: The repo directory name
        :return: The combined path
    """
    return get_config().REPOS_PATH / repo_dir


def combine_full_dir_repo(repo_dir: str, repo_name: str) -> Path:
    """
    Combine a repo directory name and repo name into a system path

        :param repo_dir: The repo directory name
        :param repo_name: The repo name
        :return: The combined path
    """
    return combine_full_dir(repo_dir) / (repo_name + ".git")


def find_dirs() -> Iterator[str]:
    """
    Find allowed directories in a repos folder

        :return: Directory path names
    """
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
    """
    Create a ssh uri for a given repository path

        :param repo_path: The repository path
        :return: the ssh uri
    """
    return get_config().REPOS_SSH_BASE + ":" +\
        str(repo_path.relative_to(get_config().REPOS_PATH)).replace("\\", "/")


def pathlib_delete_ro_file(action, name, exc):  # pragma: no cover
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


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


def path_to_tree_components(path: Path) -> Generator[None, None, PathComponent]:
    """
    Get the components of a repo tree path

        :param path: The path to split
        :yield: the PathComponent
    """
    parts = path.parts
    max_i = len(parts) - 1
    curr_path = Path()

    for i, part in enumerate(parts):
        is_end = True if max_i == i else False
        curr_path = curr_path / part
        yield PathComponent(curr_path, part, is_end)
