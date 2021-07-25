import os
import secrets
import shutil
from pathlib import Path

from quart import (Quart, abort, make_response, redirect, render_template,
                   request, url_for)
from quart_auth import (AuthManager, AuthUser, Unauthorized, login_required,
                        login_user, logout_user)

from .git.archive import ArchiveTypes, run_get_archive
from .git.log import run_get_logs
from .git.utils import find_repos, get_description, init_repo, set_description

app = Quart(__name__)
auth_manager = AuthManager(app)

REPOS_PATH = Path(os.environ["REPOS_PATH"])
# should look similar to: git@example.com
REPOS_SSH_BASE = os.environ["REPOS_SSH_BASE"]
# password preventing unwanted access
LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
app.secret_key = os.environ["SECRET_KEY"]
# this is allowing us to run through a proxy
app.config["QUART_AUTH_COOKIE_SECURE"] = False


@app.errorhandler(Unauthorized)
async def redirect_to_login(*_):
    return redirect(url_for(".do_login"))


@app.route("/login", methods=["GET", "POST"])
async def do_login():
    if request.method == "POST":
        password = (await request.form).get("password")
        if not password:
            abort(400)
        if not secrets.compare_digest(password, LOGIN_PASSWORD):
            abort(401)
        login_user(AuthUser("user"), True)
        return redirect(url_for(".directory_list"))

    return await render_template("login.html")


@app.route("/logout")
@login_required
async def do_logout():
    logout_user()
    return redirect(url_for(".do_login"))


@app.route("/")
@login_required
async def directory_list():
    return await render_template(
        "directories.html",
        dir_paths=os.listdir(REPOS_PATH)
    )

@app.route("/new", methods=["POST"])
@login_required
async def new_directory():
    repo_dir = (await request.form).get("repo-dir")

    if not repo_dir:
        abort(400)
    repo_dir = repo_dir.strip().replace(" ", "-")
    full_path = REPOS_PATH / repo_dir

    if full_path.exists():
        abort(400, "already exists")

    full_path.mkdir()

    return redirect(url_for(".repo_list", directory=repo_dir))


@app.route("/<repo_dir>/new", methods=["POST"])
@login_required
async def repo_init(repo_dir: str):
    if not (REPOS_PATH / repo_dir).exists():
        abort(404)

    repo_name = (await request.form).get("repo-name")
    if not repo_name:
        abort(400)
    repo_name = repo_name.strip().replace(" ", "-")
    if (REPOS_PATH / repo_dir / (repo_name + ".git")).exists():
        abort(400, "already exists")

    init_repo(REPOS_PATH / repo_dir, repo_name)
    return redirect(
        url_for(".repo_view", repo_dir=repo_dir, repo_name=repo_name)
    )



@app.route("/<directory>/repos")
@login_required
async def repo_list(directory):
    repo_paths = find_repos(REPOS_PATH / directory, True)
    return await render_template(
        "repos.html",
        directory=directory,
        repo_paths=repo_paths
    )


@app.route("/<repo_dir>/repos/<repo_name>")
@login_required
async def repo_view(repo_dir: str, repo_name: str):
    repo_path = REPOS_PATH / repo_dir / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)

    ssh_url = REPOS_SSH_BASE + ":" + str(repo_path.relative_to(REPOS_PATH))
    return await render_template(
        "repository.html",
        repo_dir=repo_dir,
        repo_name=repo_name,
        ssh_url=ssh_url,
        repo_description=await get_description(repo_path),
        )


@app.route("/<repo_dir>/repos/<repo_name>/delete", methods=["GET"])
@login_required
async def repo_delete(repo_dir: str, repo_name: str):
    repo_path = REPOS_PATH / repo_dir / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)
    shutil.rmtree(repo_path)
    return redirect(url_for(".repo_list", directory=repo_dir))


@app.route("/<repo_dir>/repos/<repo_name>/set-description", methods=["POST"])
@login_required
async def repo_set_description(repo_dir: str, repo_name: str):
    repo_path = REPOS_PATH / repo_dir / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)

    new_description = (await request.form).get("repo-description")
    if not new_description:
        abort(400)

    await set_description(repo_path, new_description)

    return redirect(url_for(".repo_view", repo_dir=repo_dir, repo_name=repo_name))


@app.route("/<repo_dir>/repos/<repo_name>/set-name", methods=["POST"])
@login_required
async def repo_set_name(repo_dir: str, repo_name: str):
    repo_path = REPOS_PATH / repo_dir / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)

    new_name = (await request.form).get("repo-name")
    if not new_name:
        abort(400)
    new_name = new_name.strip().replace(" ", "-")
    repo_path.rename(REPOS_PATH / repo_dir / (new_name + ".git"))

    return redirect(url_for(".repo_view", repo_dir=repo_dir, repo_name=new_name))


@app.route("/<repo_dir>/repos/<repo_name>/commits")
@login_required
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
@login_required
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
