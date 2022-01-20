from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from git_interface.branch import get_branches
from git_interface.datatypes import Log, TreeContent
from git_interface.exceptions import NoBranchesException
from git_interface.log import get_logs
from git_interface.ls import ls_tree

from .calculations import sort_repo_tree


@dataclass
class RepoContent:
    tree_ish: str
    head: str
    branches: list[str]
    root_tree: tuple[TreeContent]
    recent_log: Log


def get_repo_view_content(
        tree_ish: str,
        repo_path: Path,
        tree_path: Optional[str] = None) -> RepoContent:
    head = None
    branches = None
    root_tree = None
    recent_log = None

    try:
        head, branches = get_branches(repo_path)
    except NoBranchesException:
        pass
    else:
        if tree_ish is None:
            tree_ish = head

        branches = list(branches)
        branches.append(head)

        root_tree = ls_tree(repo_path, tree_ish, False, False, tree_path)
        root_tree = sort_repo_tree(root_tree)

        recent_log = next(get_logs(repo_path, tree_ish, 1))
    return RepoContent(tree_ish, head, branches, root_tree, recent_log)
