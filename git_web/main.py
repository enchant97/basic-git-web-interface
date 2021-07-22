import os
from pathlib import Path

from quart import Quart, abort, render_template

from .git.log import run_get_logs

app = Quart(__name__)

REPOS_PATH = Path(os.environ["REPOS_PATH"])

@app.route("/repo/<repo_name>/logs")
async def repo_logs(repo_name: str):
    repo_path = REPOS_PATH / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)
    logs = run_get_logs(repo_path)
    return await render_template(
        "logs.html",
        logs=logs,
        repo_name=repo_name
    )
