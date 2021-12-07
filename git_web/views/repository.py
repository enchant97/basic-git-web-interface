import shutil

from git_interface.branch import get_branches
from git_interface.exceptions import (GitException, NoBranchesException,
                                      PathDoesNotExistInRevException,
                                      UnknownRevisionException)
from git_interface.log import get_logs
from git_interface.ls import ls_tree
from git_interface.show import show_file
from git_interface.utils import (ArchiveTypes, clone_repo, get_archive,
                                 get_description, init_repo, run_maintenance,
                                 set_description)
from markdown_it import MarkdownIt
from quart import (Blueprint, abort, make_response, redirect, render_template,
                   request, url_for)
from quart_auth import login_required

from ..helpers import (create_ssh_uri, find_dirs, get_config, is_commit_hash,
                       is_valid_clone_url, is_valid_directory_name,
                       is_valid_repo_name, pathlib_delete_ro_file,
                       safe_combine_full_dir, safe_combine_full_dir_repo,
                       sort_repo_tree)

blueprint = Blueprint("repository", __name__)


@blueprint.get("/new")
@login_required
async def get_new_repo():
    return await render_template(
        "repository/create-repo.html",
        dir_paths=find_dirs()
    )


@blueprint.post("/new")
@login_required
async def post_new_repo():
    try:
        form = await request.form
        name = form["name"]
        directory = form["directory"]
        description = form.get("description")

        if description == "":
            description = None
        else:
            description = description.strip()

        name = name.strip().replace(" ", "-")
        if name == "":
            abort(400, "repo name/directory cannot be blank")
        if not is_valid_repo_name(name):
            abort(400, "repo name contains restricted characters")
        if not is_valid_directory_name(directory):
            abort(400, "directory name contains restricted characters")

        full_path = safe_combine_full_dir(directory)
        full_repo_path = full_path / (name + ".git")

        if not full_path.exists():
            abort(400, "directory does not exist")
        if full_repo_path.exists():
            abort(400, "repo name already exists")
    except KeyError:
        abort(400, "missing required values")
    except ValueError:
        abort(400, "invalid values in form given")

    init_repo(
        full_path,
        name,
        True,
        get_config().DEFAULT_BRANCH
    )
    if description is not None:
        set_description(full_repo_path, description)
    return redirect(url_for(".repo_view", repo_dir=directory, repo_name=name))


@blueprint.get("/new/import")
@login_required
async def get_import_repo():
    return await render_template(
        "repository/import-repo.html",
        dir_paths=find_dirs()
    )


@blueprint.post("/new/import")
@login_required
async def post_import_repo():
    try:
        form = await request.form
        url = form["import-url"]
        name = form["name"]
        directory = form["directory"]

        name = name.strip().replace(" ", "-")
        if name == "" or directory == "":
            abort(400, "repo name/directory cannot be blank")
        if not is_valid_repo_name(name):
            abort(400, "repo name contains restricted characters")
        if not is_valid_directory_name(directory):
            abort(400, "directory name contains restricted characters")

        full_path = safe_combine_full_dir(directory)
        full_repo_path = full_path / (name + ".git")

        if not full_path.exists():
            abort(400, "directory does not exist")
        if full_repo_path.exists():
            abort(400, "repo name already exists")

        if not is_valid_clone_url(url):
            abort(400, "invalid repo url given")

        clone_repo(full_repo_path, url, True)
    except KeyError:
        abort(400, "missing required values")
    except ValueError:
        abort(400, "invalid values in form given")
    except GitException:
        abort(400, "failed to clone repo")

    return redirect(url_for(".repo_view", repo_dir=directory, repo_name=name))


@blueprint.route("/<repo_dir>/<repo_name>", defaults={"branch": None})
@blueprint.route("/<repo_dir>/<repo_name>/tree/<branch>")
@login_required
async def repo_view(repo_dir: str, repo_name: str, branch: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    ssh_url = create_ssh_uri(repo_path)

    head = None
    branches = None
    root_tree = None
    recent_log = None

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
        root_tree = sort_repo_tree(root_tree)

        recent_log = next(get_logs(repo_path, branch))

    # TODO implement more intelligent readme logic
    readme_content = ""
    if head:
        try:
            content = show_file(repo_path, branch, "README.md").decode()
            md = MarkdownIt("gfm-like", {"html": False})
            readme_content = md.render(content)
        except PathDoesNotExistInRevException:
            # no readme recognised
            pass

    return await render_template(
        "repository/repository.html",
        repo_dir=repo_dir,
        repo_name=repo_name,
        curr_branch=branch,
        head=head,
        branches=branches,
        ssh_url=ssh_url,
        repo_description=get_description(repo_path),
        root_tree=root_tree,
        readme_content=readme_content,
        recent_log=recent_log,
    )


@blueprint.get("/<repo_dir>/<repo_name>/settings")
@login_required
async def repo_settings(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    head = None
    try:
        head, _ = get_branches(repo_path)
    except NoBranchesException:
        pass

    return await render_template(
        "/repository/settings.html",
        repo_dir=repo_dir,
        repo_name=repo_name,
        head=head,
    )


@blueprint.route("/<repo_dir>/<repo_name>/delete", methods=["GET"])
@login_required
async def repo_delete(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)
    shutil.rmtree(repo_path, onerror=pathlib_delete_ro_file)
    return redirect(url_for("directory.repo_list", directory=repo_dir))


@blueprint.route("/<repo_dir>/<repo_name>/set-description", methods=["POST"])
@login_required
async def repo_set_description(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    new_description = (await request.form).get("repo-description")
    if not new_description:
        abort(400, "no 'repo-description' given")

    new_description = new_description.strip()
    set_description(repo_path, new_description)

    return redirect(url_for(".repo_view", repo_dir=repo_dir, repo_name=repo_name))


@blueprint.route("/<repo_dir>/<repo_name>/set-name", methods=["POST"])
@login_required
async def repo_set_name(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    new_name = (await request.form).get("repo-name")

    if not new_name:
        abort(400, "missing 'repo-name'")
    new_name = new_name.strip().replace(" ", "-")
    if not is_valid_repo_name(new_name):
        abort(400, "repo name contains restricted characters")

    repo_path.rename(safe_combine_full_dir_repo(repo_dir, new_name))

    return redirect(url_for(".repo_view", repo_dir=repo_dir, repo_name=new_name))


@blueprint.route("/<repo_dir>/<repo_name>/maintenance")
@login_required
async def repo_maintenance_run(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)
    run_maintenance(repo_path)
    return redirect(url_for(".repo_view", repo_dir=repo_dir, repo_name=repo_name))


@blueprint.route("/<repo_dir>/<repo_name>/commits/<branch>")
@login_required
async def repo_commit_log(repo_dir: str, repo_name: str, branch: str):
    try:
        repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
        if not repo_path.exists():
            abort(404)

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

        rev_range = branch
        after_commit_hash = request.args.get("after")
        if after_commit_hash:
            if is_commit_hash(after_commit_hash):
                # TODO use <hash>^ when git-interface has parent hash detection
                rev_range = f"{after_commit_hash}"
            else:
                abort(400, "Invalid after param argument")

        logs = tuple(get_logs(repo_path, rev_range, get_config().MAX_COMMIT_LOG_COUNT))

        if after_commit_hash:
            # TODO remove when <hash>^ is used
            logs = logs[1:]

        last_commit_hash = None
        if len(logs) == get_config().MAX_COMMIT_LOG_COUNT:
            last_commit_hash = logs[-1].commit_hash

        return await render_template(
            "repository/commit_log.html",
            logs=logs,
            curr_branch=branch,
            branches=branches,
            head=head,
            repo_dir=repo_dir,
            repo_name=repo_name,
            last_commit_hash=last_commit_hash,
        )
    except UnknownRevisionException:
        abort(404)


@blueprint.route("/<repo_dir>/<repo_name>/archive.<archive_type>")
@login_required
async def repo_archive(repo_dir: str, repo_name: str, archive_type: str):
    try:
        ArchiveTypes(archive_type)
    except ValueError:
        abort(404)

    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    content = get_archive(repo_path, archive_type)
    response = await make_response(content)
    response.mimetype = "application/" + archive_type
    return response
