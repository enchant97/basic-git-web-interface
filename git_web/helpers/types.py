from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "UnknownBranchName", "PathComponent",
]


class UnknownBranchName(Exception):
    pass


@dataclass
class PathComponent:
    """
    A tree path component,
    containing the full path,
    name and whether it is the last section
    """
    full_path: Path
    name: str
    is_end: bool
