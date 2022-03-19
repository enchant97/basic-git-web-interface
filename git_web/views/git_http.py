"""
Methods for supporting git's 'Smart HTTP' protocol
"""
from functools import wraps

from git_interface.pack import ALLOWED_PACK_TYPES
from git_interface.smart_http.quart import (get_info_refs_response,
                                            post_pack_response)
from quart import Blueprint, abort, current_app, request
from quart_auth import basic_auth_required as git_auth_required

from ..helpers.config import get_config
from ..helpers.requests import ensure_repo_path_valid

blueprint = Blueprint("git_http", __name__)


def require_http_git_enabled(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if get_config().HTTP_GIT_ENABLED:
            return await current_app.ensure_async(func)(*args, **kwargs)
        abort(404, "The service 'Git Smart HTTP' has been disabled")
    return wrapper


@blueprint.post("/<repo_dir>/<repo_name>.git/<pack_type>")
@require_http_git_enabled
@git_auth_required()
async def post_pack(repo_dir: str, repo_name: str, pack_type: str):
    if pack_type not in ALLOWED_PACK_TYPES:
        abort(404)
    repo_path = ensure_repo_path_valid(repo_dir, repo_name)
    return await post_pack_response(repo_path, pack_type)


@blueprint.get("/<repo_dir>/<repo_name>.git/info/refs")
@require_http_git_enabled
@git_auth_required()
async def get_info_refs(repo_dir: str, repo_name: str):
    repo_path = ensure_repo_path_valid(repo_dir, repo_name)
    pack_type = request.args.get("service")
    if pack_type not in ALLOWED_PACK_TYPES:
        abort(403)
    return await get_info_refs_response(repo_path, pack_type)
