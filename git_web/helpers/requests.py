from http import HTTPStatus
from pathlib import Path

from quart import abort

from ..helpers.calculations import (safe_combine_full_dir,
                                    safe_combine_full_dir_repo)


def ensure_repo_dir_path_valid(repo_dir: str) -> Path:
    try:
        repo_path = safe_combine_full_dir(repo_dir)
        if not repo_path.exists():
            abort(HTTPStatus.NOT_FOUND)
        return repo_path
    except ValueError:
        abort(HTTPStatus.NOT_FOUND)


def ensure_repo_path_valid(repo_dir: str, repo_name: str) -> Path:
    try:
        repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
        if not repo_path.exists():
            abort(HTTPStatus.NOT_FOUND)
        return repo_path
    except ValueError:
        abort(HTTPStatus.NOT_FOUND)
