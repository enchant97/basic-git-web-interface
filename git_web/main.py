import os
from pathlib import Path

from quart import (Quart, abort, make_response, redirect, render_template,
                   request, url_for)

from .git.archive import ArchiveTypes, run_get_archive
from .git.log import run_get_logs
from .git.utils import find_repos, init_repo

app = Quart(__name__)

REPOS_PATH = Path(os.environ["REPOS_PATH"])
# should look similar to: git@example.com
REPOS_SSH_BASE = os.environ["REPOS_SSH_BASE"]


@app.route("/")
async def directory_list():
    return await render_template(
        "directories.html",
        dir_paths=os.listdir(REPOS_PATH)
    )

@app.route("/new", methods=["POST"])
async def new_directory():
    repo_dir = (await request.form).get("repo-dir")

    if not repo_dir:
        abort(400)

    full_path = REPOS_PATH / repo_dir

    if full_path.exists():
        abort(400, "already exists")

    full_path.mkdir()

    return redirect(url_for(".repo_list", directory=repo_dir))


@app.route("/<repo_dir>/new", methods=["POST"])
async def repo_init(repo_dir: str):
    if not (REPOS_PATH / repo_dir).exists():
        abort(404)

    repo_name = (await request.form).get("repo-name")
    if not repo_name:
        abort(400)

    if (REPOS_PATH / repo_dir / (repo_name + ".git")).exists():
        abort(400, "already exists")

    init_repo(REPOS_PATH / repo_dir, repo_name)
    return redirect(
        url_for(".repo_view", repo_dir=repo_dir, repo_name=repo_name)
    )



@app.route("/<directory>/repos")
async def repo_list(directory):
    repo_paths = find_repos(REPOS_PATH / directory, True)
    return await render_template(
        "repos.html",
        directory=directory,
        repo_paths=repo_paths
    )


@app.route("/<repo_dir>/repos/<repo_name>")
async def repo_view(repo_dir: str, repo_name: str):
    repo_path = REPOS_PATH / repo_dir / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)

    ssh_url = REPOS_SSH_BASE + ":" + str(repo_path.relative_to(REPOS_PATH))
    return await render_template(
        "repository.html",
        repo_dir=repo_dir,
        repo_name=repo_name,
        ssh_url=ssh_url
        )


@app.route("/<repo_dir>/repos/<repo_name>/commits")
async def repo_commit_log(repo_dir: str, repo_name: str):
    repo_path = REPOS_PATH / repo_dir / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)
    logs = run_get_logs(repo_path)
    return await render_template(
        "commit_log.html",
        logs=logs,
        repo_dir=repo_dir,
        repo_name=repo_name
    )


@app.route("/<repo_dir>/repos/<repo_name>/archive.<archive_type>")
async def repo_archive(repo_dir: str, repo_name: str, archive_type: str):
    try:
        ArchiveTypes(archive_type)
    except ValueError:
        abort(404)

    repo_path = REPOS_PATH / repo_dir / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)

    content = run_get_archive(repo_path, archive_type)
    response = await make_response(content)
    response.mimetype = "application/" + archive_type
    return response
