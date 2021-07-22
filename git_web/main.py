import os
from pathlib import Path

from quart import Quart, abort, render_template
from quart import make_response

from .git.archive import ArchiveTypes, run_get_archive
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


@app.route("/repo/<repo_name>/archive.<archive_type>")
async def repo_archive(repo_name: str, archive_type: str):
    try:
        ArchiveTypes(archive_type)
    except ValueError:
        abort(404)

    repo_path = REPOS_PATH / (repo_name + ".git")
    if not repo_path.exists():
        abort(404)

    content = run_get_archive(repo_path, archive_type)
    response = await make_response(content)
    response.mimetype = "application/" + archive_type
    return response
