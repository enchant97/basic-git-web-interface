import subprocess
from os import path
from pathlib import Path
from typing import Optional


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


def find_repos(repo_dir, make_relative: bool = False):
    found = subprocess.run(
        [
            "find", str(repo_dir), "-path", "*.git/*",
            "-prune", "-false", "-o", "-type", "d",
            "-name", "*.git", "-print"
        ],
        capture_output=True).stdout.decode().strip()
    found = found.split("\n")
    if make_relative:
        for path in found:
            yield Path(path).relative_to(repo_dir)
    else:
        for path in found:
            yield Path(path)
