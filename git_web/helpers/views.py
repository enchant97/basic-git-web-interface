from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from git_interface.branch import get_branches
from git_interface.datatypes import Log, TreeContent
from git_interface.exceptions import (NoBranchesException,
                                      PathDoesNotExistInRevException)
from git_interface.log import get_logs
from git_interface.ls import ls_tree
from git_interface.show import show_file
from git_interface.tag import list_tags
from quart import url_for

from .calculations import sort_repo_tree
from .content_preview import render_markdown


@dataclass
class RepoContent:
    tree_ish: str
    head: str
    branches: list[str]
    tags: list[str]
    root_tree: tuple[TreeContent]
    recent_log: Log


def get_repo_view_content(
        tree_ish: str,
        repo_path: Path,
        tree_path: Optional[str] = None) -> RepoContent:
    head = None
    branches = None
    tags = None
    root_tree = None
    recent_log = None

    try:
        head, branches = get_branches(repo_path)
        tags = list_tags(repo_path)
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
    return RepoContent(tree_ish, head, branches, tags, root_tree, recent_log)


def try_get_readme(repo_path: Path, repo_dir: str, repo_name: str, repo_content: RepoContent) -> str:
    readme_content = ""
    # TODO implement more intelligent readme logic
    if repo_content.head:
        try:
            content = show_file(repo_path, repo_content.tree_ish, "README.md").decode()
            readme_content = render_markdown(
                content,
                url_for(
                    ".get_repo_blob_file",
                    repo_dir=repo_dir,
                    repo_name=repo_name,
                    tree_ish=repo_content.tree_ish,
                    file_path=""),
                url_for(
                    ".get_repo_raw_file",
                    repo_dir=repo_dir,
                    repo_name=repo_name,
                    tree_ish=repo_content.tree_ish,
                    file_path="")
            )
        except PathDoesNotExistInRevException:
            # no readme recognised
            pass
    return readme_content
