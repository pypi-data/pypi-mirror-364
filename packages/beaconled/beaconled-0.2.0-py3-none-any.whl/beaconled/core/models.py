"""Data models for Beacon delivery analytics."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class FileStats:
    """Statistics for a single file."""

    path: str
    lines_added: int
    lines_deleted: int
    lines_changed: int


@dataclass
class CommitStats:
    """Statistics for a single commit."""

    hash: str
    author: str
    date: datetime
    message: str
    files_changed: int
    lines_added: int
    lines_deleted: int
    files: List[FileStats]


@dataclass
class RangeStats:
    """Statistics for a range of commits."""

    start_date: datetime
    end_date: datetime
    total_commits: int
    total_files_changed: int
    total_lines_added: int
    total_lines_deleted: int
    commits: List[CommitStats]
    authors: Dict[str, int]
