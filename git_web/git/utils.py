import subprocess
from pathlib import Path
from typing import Optional

import aiofiles


def init_repo(
        repo_dir: Path,
        repo_name: str,
        bare: bool = True,
        default_branch: Optional[str] = None):
    args = ["git", "init", str(repo_dir / (repo_name + ".git")), "--quiet"]
    if bare:
        args.append("--bare")
    if default_branch:
        args.append(f"--initial-branch={default_branch}")
    subprocess.run(args).check_returncode()


async def get_description(git_repo: Path) -> str:
    async with aiofiles.open(git_repo / "description", "r") as fo:
        return await fo.read()


async def set_description(git_repo: Path, description: str):
    async with aiofiles.open(git_repo / "description", "w") as fo:
        return await fo.write(description)


def run_maintenance(git_repo: Path) -> str:
    args = ["git", "-C", str(git_repo), "maintenance", "run"]
    process = subprocess.run(args, capture_output=True)
    process.check_returncode()
    return process.stdout


def find_repos(repo_dir, make_relative: bool = False):
    found = subprocess.run(
        [
            "find", str(repo_dir), "-path", "*.git/*",
            "-prune", "-false", "-o", "-type", "d",
            "-name", "*.git", "-print"
        ],
        capture_output=True).stdout.decode().strip()
    found = found.split("\n")
    if found[0] == "":
        # directory is empty
        return
    if make_relative:
        for path in found:
            yield Path(path).relative_to(repo_dir)
    else:
        for path in found:
            yield Path(path)
