from quart import Quart, redirect, url_for
from quart_auth import AuthManager, Unauthorized
from web_health_checker.contrib import quart as health_check

from . import __version__
from .helpers import get_config
from .views import auth, directory, repository

app = Quart(__name__)
auth_manager = AuthManager()


@app.errorhandler(Unauthorized)
async def redirect_to_login(*_):
    return redirect(url_for("auth.get_login"))


def create_app() -> Quart:
    # load config
    get_config()
    app.secret_key = get_config().SECRET_KEY
    # this is allowing us to run through a proxy
    app.config["QUART_AUTH_COOKIE_SECURE"] = False
    app.config["VERSION"] = __version__
    # register blueprints
    app.register_blueprint(health_check.blueprint)
    app.register_blueprint(auth.blueprint, url_prefix="/auth")
    app.register_blueprint(directory.blueprint)
    app.register_blueprint(repository.blueprint)

    auth_manager.init_app(app)
    return app
