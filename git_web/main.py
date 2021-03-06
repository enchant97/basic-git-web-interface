import sys

from quart import Quart, redirect, url_for
from quart_auth import AuthManager, Unauthorized
from web_health_checker.contrib import quart as health_check

from . import __version__
from .helpers import get_config
from .helpers.known_mimetypes import register_extra_types
from .views import auth, directory, git_http, home, repository

app = Quart(__name__)
auth_manager = AuthManager()


@app.errorhandler(Unauthorized)
async def redirect_to_login(*_):  # pragma: no cover
    return redirect(url_for("auth.get_login"))


@app.get("/favicon.ico")
async def redirect_favicon():
    return redirect(url_for("static", filename="favicon.ico"))


def create_app() -> Quart:
    # register extra MIME types
    register_extra_types()
    # load config
    config = get_config()
    app.secret_key = config.SECRET_KEY
    # this is allowing us to run through a proxy
    app.config["QUART_AUTH_COOKIE_SECURE"] = False
    app.config["QUART_AUTH_BASIC_USERNAME"] = "git"
    app.config["QUART_AUTH_BASIC_PASSWORD"] = get_config().LOGIN_PASSWORD
    app.config["VERSION"] = __version__
    app.config["SHOW_SSH_PUB"] = True if get_config().SSH_PUB_KEY_PATH else False
    app.config["SHOW_SSH_AUTHORISED"] = True if get_config().SSH_AUTH_KEYS_PATH else False
    # register blueprints
    app.register_blueprint(health_check.blueprint)
    app.register_blueprint(home.blueprint)
    app.register_blueprint(auth.blueprint, url_prefix="/auth")
    app.register_blueprint(directory.blueprint)
    app.register_blueprint(repository.blueprint)
    app.register_blueprint(git_http.blueprint)
    # register plugins
    auth_manager.init_app(app)
    # try to setup app folders
    try:
        config.REPOS_PATH.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(
            f"Not enough permissions for repos path '{config.REPOS_PATH}'",
            file=sys.stderr
        )
        sys.exit(1)
    return app
