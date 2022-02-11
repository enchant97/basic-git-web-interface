"""
Methods for supporting git's 'Smart HTTP' protocol
"""
import asyncio
from collections.abc import AsyncGenerator
from functools import wraps
from pathlib import Path

from async_timeout import timeout
from git_interface.exceptions import BufferedProcessError
from quart import Blueprint, abort, current_app, make_response, request
from quart_auth import basic_auth_required as git_auth_required

from ..helpers.requests import ensure_repo_path_valid
from ..helpers.config import get_config

blueprint = Blueprint("git_http", __name__)


def require_http_git_enabled(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if get_config().HTTP_GIT_ENABLED:
            return await current_app.ensure_async(func)(*args, **kwargs)
        abort(404, "The service 'Git Smart HTTP' has been disabled")
    return wrapper


async def process_pack_exchange(
        repo_path: Path,
        pack_type: str,
        client_data_stream: AsyncGenerator[bytes, None],
        advertise_refs: bool = False) -> AsyncGenerator[bytes, None]:
    """
    Communicate with the git commands: upload-pack and receive-pack
    """
    args = ["git", pack_type.removeprefix("git-"), "--stateless-rpc"]
    advertisement = None

    # If refs are being requested
    if advertise_refs:
        args.append("--http-backend-info-refs")
        args.append("--advertise-refs")

        # The service type prefixed with the total line length
        advertisement = f"# service={pack_type}\n".encode()
        hex_len = hex(len(advertisement) + 4)[2:]
        hex_len = hex_len.zfill(4)
        advertisement = hex_len.encode() + advertisement + b"0000"

    args.append(str(repo_path))

    process = await asyncio.create_subprocess_exec(
        args[0], *args[1:],
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    async for chunk in client_data_stream:
        process.stdin.write(chunk)
    process.stdin.write_eof()

    if advertisement:
        yield advertisement

    async for chunk in process.stdout:
        yield chunk

    return_code = await process.wait()
    if return_code != 0:
        raise BufferedProcessError(await process.stderr.read(), return_code)


@blueprint.post("/<repo_dir>/<repo_name>.git/git-<pack_type>-pack")
@require_http_git_enabled
@git_auth_required()
async def post_pack(repo_dir: str, repo_name: str, pack_type: str):
    if pack_type not in ("upload", "receive"):
        abort(404)
    repo_path = ensure_repo_path_valid(repo_dir, repo_name)

    async with timeout(current_app.config["BODY_TIMEOUT"]):
        response = await make_response(process_pack_exchange(
            repo_path,
            f"git-{pack_type}-pack",
            request.body,
        ))
    response.content_type = f"application/x-git-{pack_type}-pack-result"
    response.headers.add_header("Cache-Control", "no-store")
    response.headers.add_header("Expires", "0")

    return response


@blueprint.get("/<repo_dir>/<repo_name>.git/info/refs")
@require_http_git_enabled
@git_auth_required()
async def get_info_refs(repo_dir: str, repo_name: str):
    repo_path = ensure_repo_path_valid(repo_dir, repo_name)

    pack_type = request.args.get("service")

    if pack_type not in ("git-upload-pack", "git-receive-pack"):
        abort(404)

    async with timeout(current_app.config["BODY_TIMEOUT"]):
        response = await make_response(process_pack_exchange(
            repo_path,
            pack_type,
            request.body,
            True
        ))
    response.content_type = f"application/x-{pack_type}-advertisement"
    response.headers.add_header("Cache-Control", "no-store")
    response.headers.add_header("Expires", "0")

    return response
