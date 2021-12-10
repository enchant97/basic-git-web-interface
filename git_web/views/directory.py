from quart import Blueprint, abort, redirect, render_template, request, url_for
from quart.helpers import flash
from quart_auth import login_required

from ..helpers import (does_path_contain, find_repos, is_name_reserved,
                       is_valid_directory_name, safe_combine_full_dir)

blueprint = Blueprint("directory", __name__)


@blueprint.get("/new-dir")
@login_required
async def get_new_dir():
    return await render_template("directory/create-dir.html")


@blueprint.post("/new-dir")
@login_required
async def post_new_dir():
    repo_dir = (await request.form).get("name")

    if not repo_dir:
        abort(400, "directory name missing")
    repo_dir = repo_dir.strip().replace(" ", "-")
    if not is_valid_directory_name(repo_dir):
        await flash("Directory name contains restricted characters", "error")
        return redirect(url_for(".get_new_dir"))
    if is_name_reserved(repo_dir):
        await flash("Repo directory is reserved", "error")
        return redirect(url_for(".get_new_dir"))

    full_path = safe_combine_full_dir(repo_dir)

    if full_path.exists():
        await flash("Directory already exists", "error")
        return redirect(url_for(".get_new_dir"))

    full_path.mkdir()

    return redirect(url_for(".repo_list", directory=repo_dir))


@blueprint.get("/<directory>/delete")
@login_required
async def get_dir_delete(directory: str):
    full_path = safe_combine_full_dir(directory)
    if not full_path.exists():
        await flash("Directory does not exist", "error")
        return redirect(url_for("home.index"))
    try:
        next(full_path.iterdir())
    except StopIteration:
        full_path.rmdir()
    else:
        await flash("Directory not empty", "error")
        return redirect(url_for(".repo_list", directory=directory))
    return redirect(url_for("home.index"))


@blueprint.route("/<directory>")
@login_required
async def repo_list(directory):
    search_query = request.args.get("q", "").strip()

    repo_paths = find_repos(safe_combine_full_dir(directory), True)

    if search_query:
        # only filter repo list if search was entered
        repo_paths = filter(lambda path: does_path_contain(path, search_query), repo_paths)

    repo_paths = tuple(sorted(repo_paths))

    # if there is only one repo left navigate to it instead
    if len(repo_paths) == 1:
        return redirect(url_for(
            "repository.repo_view",
            repo_dir=directory,
            repo_name=repo_paths[0].stem
        ))

    return await render_template(
        "directory/repos.html",
        directory=directory,
        repo_paths=repo_paths,
        search_query=search_query
    )
