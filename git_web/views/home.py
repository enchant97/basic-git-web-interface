from quart import Blueprint, redirect, render_template, request, url_for
from quart.helpers import flash
from quart_auth import login_required
from werkzeug.exceptions import abort

from ..helpers import find_dirs, get_config

blueprint = Blueprint("home", __name__)


@blueprint.get("/")
async def index():
    return await render_template(
        "home/index.html",
        dir_paths=sorted(find_dirs())
    )


@blueprint.get("/settings")
@login_required
async def get_settings():
    ssh_public_key = ""
    ssh_authorised_keys = ""
    if get_config().SSH_PUB_KEY_PATH:
        with open(get_config().SSH_PUB_KEY_PATH, "r") as fo:
            ssh_public_key = fo.read()
    try:
        if get_config().SSH_AUTH_KEYS_PATH:
            with open(get_config().SSH_AUTH_KEYS_PATH, "r") as fo:
                ssh_authorised_keys = fo.read()
    except FileNotFoundError:
        pass
    return await render_template(
        "home/settings.html",
        ssh_public_key=ssh_public_key,
        ssh_authorised_keys=ssh_authorised_keys,
    )


@blueprint.post("/settings/update-ssh-authorised-keys")
@login_required
async def post_update_ssh_authorised_keys():
    if not get_config().SSH_AUTH_KEYS_PATH:
        await flash("SSH key access has been disabled in server config", "error")
        return redirect(url_for(".get_settings"))
    try:
        ssh_authorised_keys = (await request.form)["ssh-authorised-keys"]

        with open(get_config().SSH_AUTH_KEYS_PATH, "w") as fo:
            fo.write(ssh_authorised_keys)

        await flash("updated authorised ssh keys", "ok")
    except KeyError:
        abort(400, "missing required 'ssh-authorised-keys'")
    return redirect(url_for(".get_settings"))
