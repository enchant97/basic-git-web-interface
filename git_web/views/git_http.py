"""
Methods for supporting git's 'Smart HTTP' protocol
"""
import asyncio
import gzip
from collections.abc import AsyncGenerator
from functools import wraps
from pathlib import Path

from git_interface.exceptions import BufferedProcessError
from quart import Blueprint, abort, make_response, request, current_app
from quart_auth import basic_auth_required as git_auth_required

from ..helpers import safe_combine_full_dir_repo
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
        client_data: bytes,
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

    process.stdin.write(client_data)
    process.stdin.write_eof()

    if advertisement:
        yield advertisement

    async for chunk in process.stdout:
        yield chunk

    return_code = await process.wait()
    if return_code != 0:
        raise BufferedProcessError(await process.stderr.read(), return_code)


async def request_body_uncompressed() -> bytes:
    """
    Ensure that the provided body is not compressed with gzip

        :return: The body
    """
    # TODO use a AsyncGenerator instead
    # Ref Docs: https://pgjones.gitlab.io/quart/how_to_guides/request_body.html#advanced-usage

    raw_data: bytes = await request.get_data(
        cache=False,
        as_text=False,
        parse_form_data=False
    )

    if request.headers.get("HTTP_CONTENT_ENCODING") == "gzip":
        return gzip.decompress(raw_data)

    return raw_data


@blueprint.post("/<repo_dir>/<repo_name>.git/git-<pack_type>-pack")
@require_http_git_enabled
@git_auth_required()
async def post_pack(repo_dir: str, repo_name: str, pack_type: str):
    if pack_type not in ("upload", "receive"):
        abort(404)
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    response = await make_response(process_pack_exchange(
        repo_path,
        f"git-{pack_type}-pack",
        await request_body_uncompressed(),
    ))
    response.content_type = f"application/x-git-{pack_type}-pack-result"
    response.headers.add_header("Cache-Control", "no-store")
    response.headers.add_header("Expires", "0")

    return response


@blueprint.get("/<repo_dir>/<repo_name>.git/info/refs")
@require_http_git_enabled
@git_auth_required()
async def get_info_refs(repo_dir: str, repo_name: str):
    repo_path = safe_combine_full_dir_repo(repo_dir, repo_name)
    if not repo_path.exists():
        abort(404)

    pack_type = request.args.get("service")

    if pack_type not in ("git-upload-pack", "git-receive-pack"):
        abort(404)

    response = await make_response(process_pack_exchange(
        repo_path,
        pack_type,
        await request_body_uncompressed(),
        True
    ))
    response.content_type = f"application/x-{pack_type}-advertisement"
    response.headers.add_header("Cache-Control", "no-store")
    response.headers.add_header("Expires", "0")

    return response
