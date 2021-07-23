import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Log:
    commit_hash: str
    author_email: str
    commit_date: datetime
    subject: str


def process_log(stdout_line: str):
    parts = stdout_line.split(";;")
    if len(parts) != 4:
        raise ValueError("invalid log line: {stdout_line}")
    return Log(
        parts[0],
        parts[1],
        datetime.fromisoformat(parts[2]),
        parts[3]
    )


def process_logs(stdout: str):
    log_lines = stdout.strip().split("\n")
    return map(process_log, log_lines)


def run_get_logs(git_repo: Path):
    process_status = subprocess.run(
        ["git", "-C", str(git_repo), "log", "--pretty=%H;;%ae;;%cI;;%s"],
        capture_output=True)
    # TODO handle empty repos
    stdout = process_status.stdout.decode()
    return process_logs(stdout)
