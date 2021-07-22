import subprocess
from pathlib import Path
from enum import Enum

class ArchiveTypes(Enum):
    TAR = "tar"
    TAR_GZ = "tar.gz"
    ZIP = "zip"


def run_get_archive(git_repo: Path, archive_type: ArchiveTypes) -> bytes:
    # this allows for strings to be passed
    if isinstance(archive_type, ArchiveTypes):
        archive_type = archive_type.value
    return subprocess.run(
        ["git", "-C", str(git_repo), "archive", f"--format={archive_type}", "HEAD"],
        capture_output=True).stdout
