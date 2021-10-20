import os
import secrets
import shutil

from git_interface.branch import get_branches
from git_interface.exceptions import (NoBranchesException,
                                      UnknownRevisionException)
from git_interface.log import get_logs
from git_interface.ls import ls_tree
from git_interface.utils import (ArchiveTypes, get_archive, get_description,
                                 init_repo, run_maintenance, set_description)
from quart import (Quart, abort, make_response, redirect, render_template,
                   request, url_for)
from quart_auth import (AuthManager, AuthUser, Unauthorized, login_required,
                        login_user, logout_user)

from .helpers import find_repos, get_config, is_allowed_dir

app = Quart(__name__)
auth_manager = AuthManager(app)

# the default branch name
DEFAULT_BRANCH = get_config().DEFAULT_BRANCH
# the root directory where repos will be stored
REPOS_PATH = get_config().REPOS_PATH
# should look similar to: git@example.com
REPOS_SSH_BASE = get_config().REPOS_SSH_BASE
# password preventing unwanted access
LOGIN_PASSWORD = get_config().LOGIN_PASSWORD
app.secret_key = get_config().SECRET_KEY
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
        dir_paths=filter(is_allowed_dir, next(os.walk(REPOS_PATH))[1])
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

    init_repo(REPOS_PATH / repo_dir, repo_name, True, DEFAULT_BRANCH)
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


@app.route("/<repo_dir>/repos/<repo_name>/", defaults={"branch": None})
@app.route("/<repo_dir>/repos/<repo_name>/tree/<branch>")
@login_required
async def repo_view(repo_dir: str, repo_name: str, branch: str):
    repo_path = REPOS_PATH / repo_dir / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)

    ssh_url = REPOS_SSH_BASE + ":" + str(repo_path.relative_to(REPOS_PATH))

    head = None
    branches = None

    try:
        head, branches = get_branches(repo_path)
    except NoBranchesException:
        pass
    else:
        if branch is None:
            branch = head
        elif branch not in branches:
            if head != branch:
                abort(404)

        branches = list(branches)
        branches.append(head)

    root_tree = ls_tree(repo_path, branch, False, False)

    return await render_template(
        "repository.html",
        repo_dir=repo_dir,
        repo_name=repo_name,
        curr_branch=branch,
        head=head,
        branches=branches,
        ssh_url=ssh_url,
        repo_description=get_description(repo_path),
        root_tree=root_tree,
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

    set_description(repo_path, new_description)

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


@app.route("/<repo_dir>/repos/<repo_name>/maintenance")
@login_required
async def repo_maintenance_run(repo_dir: str, repo_name: str):
    repo_path = REPOS_PATH / repo_dir / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)
    run_maintenance(repo_path)
    return redirect(url_for(".repo_view", repo_dir=repo_dir, repo_name=repo_name))


@app.route("/<repo_dir>/repos/<repo_name>/commits/<branch>")
@login_required
async def repo_commit_log(repo_dir: str, repo_name: str, branch: str):
    try:
        repo_path = REPOS_PATH / repo_dir / (repo_name + ".git")
        if not repo_path.exists():
            abort(404)
        logs = get_logs(repo_path, branch)
        return await render_template(
            "commit_log.html",
            logs=logs,
            curr_branch=branch,
            repo_dir=repo_dir,
            repo_name=repo_name
        )
    except UnknownRevisionException:
        abort(404)


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

    content = get_archive(repo_path, archive_type)
    response = await make_response(content)
    response.mimetype = "application/" + archive_type
    return response
