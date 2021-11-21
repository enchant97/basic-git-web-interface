from quart import Blueprint, abort, redirect, render_template, request, url_for
from quart_auth import login_required

from ..helpers import combine_full_dir, find_dirs, find_repos

blueprint = Blueprint("directory", __name__)


@blueprint.route("/")
@login_required
async def directory_list():
    return await render_template(
        "directory/directories.html",
        dir_paths=find_dirs()
    )


@blueprint.get("/new-dir")
@login_required
async def get_new_dir():
    return await render_template("directory/create-dir.html")


@blueprint.post("/new-dir")
@login_required
async def post_new_dir():
    repo_dir = (await request.form).get("name")

    if not repo_dir:
        abort(400)
    repo_dir = repo_dir.strip().replace(" ", "-")
    full_path = combine_full_dir(repo_dir)

    if full_path.exists():
        abort(400, "already exists")

    full_path.mkdir()

    return redirect(url_for(".repo_list", directory=repo_dir))


@blueprint.get("/<directory>/delete")
@login_required
async def get_dir_delete(directory: str):
    full_path = combine_full_dir(directory)
    if not full_path.exists():
        abort(400, "directory does not exist")
    try:
        next(full_path.iterdir())
    except StopIteration:
        full_path.rmdir()
    else:
        abort(400, "directory not empty")
    return redirect(url_for(".directory_list"))


@blueprint.route("/<directory>")
@login_required
async def repo_list(directory):
    repo_paths = find_repos(combine_full_dir(directory), True)
    return await render_template(
        "directory/repos.html",
        directory=directory,
        repo_paths=repo_paths
    )
