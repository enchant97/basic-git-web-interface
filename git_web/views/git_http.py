import re

from quart import Blueprint, abort, request, send_file
from quart_auth import basic_auth_required as git_auth_required

from ..helpers import safe_combine_full_dir_repo

blueprint = Blueprint("git_http", __name__)


@blueprint.post("/<repo_dir>/<repo_name>.git/git-upload-pack")
@git_auth_required()
async def post_upload_pack():
    # TODO implement
    abort(501)


@blueprint.post("/<repo_dir>/<repo_name>.git/git-receive-pack")
@git_auth_required()
async def post_receive_pack():
    # TODO implement
    abort(501)


@blueprint.get("/<repo_dir>/<repo_name>.git/info/refs")
@git_auth_required()
async def get_info_refs(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    pack_type = (await request.form).get("service")

    if pack_type is None:
        return await send_file(repo_path / "info/refs", "text/plain")

    # TODO handle specific pack-types
    abort(400)


@blueprint.get("/<repo_dir>/<repo_name>.git/HEAD")
@git_auth_required()
async def get_head(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    head_path = repo_path / "HEAD"
    if not head_path.exists():
        abort(404)

    return await send_file(head_path)


@blueprint.get("/<repo_dir>/<repo_name>.git/objects/info/alternates")
@git_auth_required()
async def get_obj_info_alt(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    file_path = repo_path / "objects/info/alternates"
    if not file_path.exists():
        abort(404)

    return await send_file(file_path, "text/plain")


@blueprint.get("/<repo_dir>/<repo_name>.git/objects/info/http-alternates")
@git_auth_required()
async def get_obj_info_http_alt(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    file_path = repo_path / "objects/info/http-alternates"
    if not file_path.exists():
        abort(404)

    return await send_file(file_path, "text/plain")


@blueprint.get("/<repo_dir>/<repo_name>.git/objects/info/packs")
@git_auth_required()
async def get_obj_info_packs(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    file_path = repo_path / "objects/info/packs"
    if not file_path.exists():
        abort(404)

    return await send_file(file_path, "text/plain")


@blueprint.get("/<repo_dir>/<repo_name>.git/objects/info/<file_name>")
@git_auth_required()
async def get_obj_info_file_files(repo_dir: str, repo_name: str, file_name: str):
    if not re.match(r"[^\/]+", file_name):
        abort(404)
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    file_path = repo_path / f"objects/info/{file_name}"
    if not file_path.exists():
        abort(404)

    return await send_file(file_path, "text/plain")


@blueprint.get("/<repo_dir>/<repo_name>.git/objects/<obj_hash_1>/<obj_hash_2>")
@git_auth_required()
async def get_loose_obj(repo_dir: str, repo_name: str, obj_hash_1, obj_hash_2: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    obj_hash_1_match = re.match(r"[0-9a-f]{2}", obj_hash_1)
    obj_hash_2_match = re.match(r"[0-9a-f]{38}", obj_hash_2)
    if None in (obj_hash_1_match, obj_hash_2_match):
        abort(404)

    obj_path = repo_path / "objects" / obj_hash_1 / obj_hash_2
    if not obj_path.exists():
        abort(404)

    # TODO add permanent caching
    return await send_file(obj_path, "application/x-git-loose-object")


@blueprint.get("/<repo_dir>/<repo_name>.git/objects/pack/pack-<obj_hash>.pack")
@git_auth_required()
async def get_obj_pack(repo_dir: str, repo_name: str, obj_hash: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    obj_hash_match = re.match(r"[0-9a-f]{40}", obj_hash)
    if not repo_path.exists() or obj_hash_match is None:
        abort(404)
    file_path = repo_path / f"objects/pack/pack-{obj_hash}.pack"
    if not file_path.exists():
        abort(404)

    # TODO add permanent caching
    return await send_file(file_path, "application/x-git-packed-objects")

@blueprint.get("/<repo_dir>/<repo_name>.git/objects/pack/pack-<obj_hash>.idx")
@git_auth_required()
async def get_obj_pack_idx(repo_dir: str, repo_name: str, obj_hash: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    obj_hash_match = re.match(r"[0-9a-f]{40}", obj_hash)
    if not repo_path.exists() or obj_hash_match is None:
        abort(404)
    file_path = repo_path / f"objects/pack/pack-{obj_hash}.idx"
    if not file_path.exists():
        abort(404)

    # TODO add permanent caching
    return await send_file(file_path, "application/x-git-packed-objects-toc")
