from quart import Blueprint, render_template
from ..helpers import find_dirs


blueprint = Blueprint("home", __name__)


@blueprint.get("/")
async def index():
    return await render_template(
        "home/index.html",
        dir_paths=sorted(find_dirs())
    )
