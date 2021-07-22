import os
from pathlib import Path

from quart import (Quart, abort, make_response, redirect, render_template,
                   url_for)

from .git.archive import ArchiveTypes, run_get_archive
from .git.log import run_get_logs
from .git.utils import find_repos, init_repo

app = Quart(__name__)

REPOS_PATH = Path(os.environ["REPOS_PATH"])


@app.route("/repo")
async def repo_list():
    repo_paths = find_repos(REPOS_PATH, True)
    return await render_template(
        "repos.html",
        repo_paths=repo_paths
    )


@app.route("/repo/<repo_name>/logs")
async def repo_logs(repo_name: str):
    repo_path = REPOS_PATH / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)
    logs = run_get_logs(repo_path)
    return await render_template(
        "logs.html",
        logs=logs,
        repo_name=repo_name
    )


@app.route("/repo/<repo_name>/archive.<archive_type>")
async def repo_archive(repo_name: str, archive_type: str):
    try:
        ArchiveTypes(archive_type)
    except ValueError:
        abort(404)

    repo_path = REPOS_PATH / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)

    content = run_get_archive(repo_path, archive_type)
    response = await make_response(content)
    response.mimetype = "application/" + archive_type
    return response


@app.route("/init/<repo_name>")
async def repo_init(repo_name: str):
    if (REPOS_PATH / (repo_name + ".git")).exists():
        abort(400, "already exists")
    init_repo(REPOS_PATH, repo_name)
    return redirect(url_for(".repo_logs", repo_name=repo_name))
