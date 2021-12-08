import secrets

from quart import Blueprint, abort, redirect, render_template, request, url_for
from quart_auth import AuthUser, login_required, login_user, logout_user

from ..helpers import get_config

blueprint = Blueprint("auth", __name__)


@blueprint.get("/login")
async def get_login():
    return await render_template("auth/login.html")


@blueprint.post("/login")
async def post_login():
    password = (await request.form).get("password")
    if not password:
        abort(400)
    if not secrets.compare_digest(password, get_config().LOGIN_PASSWORD):
        abort(401)
    login_user(AuthUser("user"), True)
    return redirect(url_for("home.index"))


@blueprint.route("/logout")
@login_required
async def do_logout():
    logout_user()
    return redirect(url_for(".get_login"))
