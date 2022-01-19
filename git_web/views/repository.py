import shutil
from pathlib import Path
from typing import Optional

from git_interface.branch import get_branches
from git_interface.cat_file import get_object_size
from git_interface.datatypes import Log, TreeContent
from git_interface.exceptions import (GitException, NoBranchesException,
                                      PathDoesNotExistInRevException,
                                      UnknownRefException,
                                      UnknownRevisionException)
from git_interface.log import get_logs
from git_interface.ls import ls_tree
from git_interface.rev_list import get_commit_count
from git_interface.show import show_file
from git_interface.symbolic_ref import change_active_branch
from git_interface.utils import (ArchiveTypes, clone_repo, get_archive,
                                 get_description, init_repo, run_maintenance,
                                 set_description)
from quart import (Blueprint, abort, make_response, redirect, render_template,
                   request, url_for)
from quart.helpers import flash
from quart_auth import login_required

from ..helpers import (MAX_BLOB_SIZE, UnknownBranchName, create_ssh_uri,
                       find_dirs, get_config, guess_mimetype, highlight_by_ext,
                       is_commit_hash, is_name_reserved, is_valid_clone_url,
                       is_valid_directory_name, is_valid_repo_name,
                       path_to_tree_components, pathlib_delete_ro_file,
                       render_markdown, safe_combine_full_dir,
                       safe_combine_full_dir_repo, sort_repo_tree)

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
            await flash("Repo name/directory cannot be blank", "error")
            return redirect(url_for(".get_new_repo"))
        if not is_valid_repo_name(name):
            await flash("Repo name contains restricted characters", "error")
            return redirect(url_for(".get_new_repo"))
        if not is_valid_directory_name(directory):
            await flash("Directory name contains restricted characters", "error")
            return redirect(url_for(".get_new_repo"))
        if is_name_reserved(name):
            await flash("Repo name is reserved", "error")
            return redirect(url_for(".get_new_repo"))

        full_path = safe_combine_full_dir(directory)
        full_repo_path = full_path / (name + ".git")

        if not full_path.exists():
            await flash("Directory does not exist", "error")
            return redirect(url_for(".get_new_repo"))
        if full_repo_path.exists():
            await flash("Repo name already exists", "error")
            return redirect(url_for(".get_new_repo"))
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


@blueprint.get("/import")
@login_required
async def get_import_repo():
    return await render_template(
        "repository/import-repo.html",
        dir_paths=find_dirs()
    )


@blueprint.post("/import")
@login_required
async def post_import_repo():
    try:
        form = await request.form
        url = form["import-url"]
        name = form["name"]
        directory = form["directory"]

        name = name.strip().replace(" ", "-")
        if name == "" or directory == "":
            await flash("Repo name/directory cannot be blank", "error")
            return redirect(url_for(".get_import_repo"))
        if not is_valid_repo_name(name):
            await flash("Repo name contains restricted characters", "error")
            return redirect(url_for(".get_import_repo"))
        if not is_valid_directory_name(directory):
            await flash("Directory name contains restricted characters", "error")
            return redirect(url_for(".get_import_repo"))
        if is_name_reserved(name):
            await flash("Repo name is reserved", "error")
            return redirect(url_for(".get_import_repo"))

        full_path = safe_combine_full_dir(directory)
        full_repo_path = full_path / (name + ".git")

        if not full_path.exists():
            await flash("Directory does not exist", "error")
            return redirect(url_for(".get_import_repo"))
        if full_repo_path.exists():
            await flash("Repo name already exists", "error")
            return redirect(url_for(".get_import_repo"))
        if not is_valid_clone_url(url):
            await flash("Invalid repo url given", "error")
            return redirect(url_for(".get_import_repo"))

        clone_repo(full_repo_path, url, True)
    except KeyError:
        abort(400, "missing required values")
    except ValueError:
        abort(400, "invalid values in form given")
    except GitException:
        abort(400, "failed to clone repo")

    return redirect(url_for(".repo_view", repo_dir=directory, repo_name=name))


def get_repo_view_content(
        branch: str,
        repo_path: Path,
        tree_path: Optional[str] = None) -> tuple[str, list[str], tuple[TreeContent], Log]:
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
                raise UnknownBranchName()

        branches = list(branches)
        branches.append(head)

        root_tree = ls_tree(repo_path, branch, False, False, tree_path)
        root_tree = sort_repo_tree(root_tree)

        recent_log = next(get_logs(repo_path, branch, 1))
    return head, branches, root_tree, recent_log


@blueprint.route("/<repo_dir>/<repo_name>", defaults={"branch": None})
@blueprint.route("/<repo_dir>/<repo_name>/tree/<branch>")
@login_required
async def repo_view(repo_dir: str, repo_name: str, branch: str):
    try:
        repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
        if not repo_path.exists():
            abort(404)

        ssh_url = create_ssh_uri(repo_path)

        head, branches, root_tree, recent_log = get_repo_view_content(branch, repo_path)

        if branch is None:
            branch = head

        commit_count = get_commit_count(repo_path, branch)

        # TODO implement more intelligent readme logic
        readme_content = ""
        if head:
            try:
                content = show_file(repo_path, branch, "README.md").decode()
                readme_content = render_markdown(
                    content,
                    url_for(
                        ".get_repo_blob_file",
                        repo_dir=repo_dir,
                        repo_name=repo_name,
                        branch=branch,
                        file_path=""),
                    url_for(
                        ".get_repo_raw_file",
                        repo_dir=repo_dir,
                        repo_name=repo_name,
                        branch=branch,
                        file_path="")
                )
            except PathDoesNotExistInRevException:
                # no readme recognised
                pass
    except (ValueError, UnknownBranchName):
        abort(404)
    else:
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
            tree_path="",
            commit_count=commit_count,
        )


@blueprint.get("/<repo_dir>/<repo_name>/tree/<branch>/<path:tree_path>")
@login_required
async def get_repo_tree(repo_dir: str, repo_name: str, branch: str, tree_path: str):
    try:
        repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
        if not repo_path.exists():
            abort(404)

        if not tree_path.endswith("/"):
            tree_path += "/"

        head, branches, root_tree, recent_log = get_repo_view_content(branch, repo_path, tree_path)

        split_path = path_to_tree_components(Path(tree_path))

    except (ValueError, UnknownBranchName):
        abort(404)
    else:
        return await render_template(
            "repository/tree.html",
            repo_dir=repo_dir,
            repo_name=repo_name,
            curr_branch=branch,
            head=head,
            branches=branches,
            root_tree=root_tree,
            recent_log=recent_log,
            tree_path=tree_path,
            split_path=split_path,
        )


@blueprint.get("/<repo_dir>/<repo_name>/blob/<branch>/<path:file_path>")
@login_required
async def get_repo_blob_file(repo_dir: str, repo_name: str, branch: str, file_path: str):
    try:
        repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
        if not repo_path.exists():
            abort(404)

        file_path = file_path.replace("\\", "/")  # fixes issue when running server on Windows
        head, branches, root_tree, recent_log = get_repo_view_content(branch, repo_path, file_path)

        split_path = path_to_tree_components(Path(file_path))

        content_type = None
        content = None

        mimetype = guess_mimetype(file_path)

        if mimetype == None:
            pass
        elif mimetype.startswith("image"):
            content_type = "IMAGE"
            content = url_for(
                ".get_repo_raw_file", repo_dir=repo_dir,
                repo_name=repo_name, branch=branch,
                file_path=file_path
            )
        elif mimetype.startswith("text"):
            if get_object_size(repo_path, branch, file_path) < MAX_BLOB_SIZE:
                content = show_file(repo_path, branch, file_path).decode()

                if mimetype.endswith("markdown"):
                    content_type = "HTML"
                    content = render_markdown(
                        content,
                        url_relative_to_raw=url_for(
                            ".get_repo_raw_file",
                            repo_dir=repo_dir,
                            repo_name=repo_name,
                            branch=branch,
                            file_path=""
                        )
                    )
                else:
                    content_type = "TEXT"
                    content = highlight_by_ext(content, file_path)

        return await render_template(
            "repository/blob.html",
                repo_dir=repo_dir,
                repo_name=repo_name,
                curr_branch=branch,
                head=head,
                branches=branches,
                root_tree=root_tree,
                recent_log=recent_log,
                tree_path=file_path,
                content_type=content_type,
                content=content,
                split_path=split_path
        )
    except (ValueError, PathDoesNotExistInRevException):
        abort(404)


@blueprint.get("/<repo_dir>/<repo_name>/raw/<branch>/<path:file_path>")
@login_required
async def get_repo_raw_file(repo_dir: str, repo_name: str, branch: str, file_path: str):
    try:
        repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
        if not repo_path.exists():
            abort(404)

        file_path = file_path.replace("\\", "/")  # fixes issue when running server on Windows

        content = show_file(repo_path, branch, file_path)
        raw_response = await make_response(content)
        mimetype = guess_mimetype(file_path)
        raw_response.mimetype = mimetype if mimetype is not None else "application/octet-stream"

        return raw_response
    except (ValueError, PathDoesNotExistInRevException):
        abort(404)


@blueprint.get("/<repo_dir>/<repo_name>/settings")
@login_required
async def repo_settings(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    head = None
    branches = None
    try:
        head, branches = get_branches(repo_path)
    except NoBranchesException:
        pass

    description = get_description(repo_path)

    return await render_template(
        "/repository/settings.html",
        repo_dir=repo_dir,
        repo_name=repo_name,
        head=head,
        branches=branches,
        description=description,
    )


@blueprint.post("/<repo_dir>/<repo_name>/change-head")
@login_required
async def post_repo_change_head(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    try:
        new_head = (await request.form)["repo-head"]

        head, branches = get_branches(repo_path)

        if head in branches:
            # skip as the head is already set
            pass
        elif new_head not in branches:
            raise UnknownRefException()
        else:
            change_active_branch(repo_path, new_head)
    except KeyError:
        await flash("missing required fields 'repo-head'", "error")
    except NoBranchesException:
        await flash("Repository has no branches yet", "error")
    except UnknownRefException:
        await flash("Unknown branch name", "error")
    finally:
        return redirect(url_for(".repo_settings", repo_dir=repo_dir, repo_name=repo_name))


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

    return redirect(url_for(".repo_settings", repo_dir=repo_dir, repo_name=repo_name))


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
        await flash("Repo name contains restricted characters", "error")
        return redirect(url_for(".repo_settings", repo_dir=repo_dir, repo_name=new_name))
    if is_name_reserved(new_name):
        await flash("Repo name is reserved", "error")
        return redirect(url_for(".repo_settings", repo_dir=repo_dir, repo_name=new_name))

    repo_path.rename(safe_combine_full_dir_repo(repo_dir, new_name))

    return redirect(url_for(".repo_settings", repo_dir=repo_dir, repo_name=new_name))


@blueprint.route("/<repo_dir>/<repo_name>/maintenance")
@login_required
async def repo_maintenance_run(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)
    run_maintenance(repo_path)
    await flash("maintenance running", "ok")
    return redirect(url_for(".repo_settings", repo_dir=repo_dir, repo_name=repo_name))


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
                rev_range = f"{after_commit_hash}^"
            else:
                abort(400, "Invalid after param argument")

        try:
            logs = tuple(get_logs(repo_path, rev_range,
                        get_config().MAX_COMMIT_LOG_COUNT))
        except UnknownRevisionException:
            logs = tuple()

        last_commit_hash = None
        if len(logs) > 0:
            if logs[-1].parent_hash:
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
