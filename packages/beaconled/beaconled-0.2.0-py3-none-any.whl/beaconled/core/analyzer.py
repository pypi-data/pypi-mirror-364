"""Git repository analyzer."""

import os
import subprocess
from datetime import datetime
from pathlib import Path

from .models import CommitStats, FileStats, RangeStats


class GitAnalyzer:
    """Analyzes git repository statistics."""

    def __init__(self, repo_path: str = "."):
        """Initialize analyzer with repository path."""
        self.repo_path = self._validate_repo_path(repo_path)

    def _validate_repo_path(self, repo_path: str) -> str:
        """Validate and sanitize repository path."""
        try:
            path = Path(repo_path).resolve()
            
            # Ensure path exists and is a directory
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Repository path does not exist: {repo_path}")
            
            # Ensure it's within allowed boundaries (prevent directory traversal)
            cwd = Path.cwd().resolve()
            if not str(path).startswith(str(cwd)):
                raise ValueError("Repository path must be within current working directory")
            
            # Check if it's actually a git repository
            git_dir = path / '.git'
            if not git_dir.exists():
                raise ValueError(f"Not a git repository: {repo_path}")
                
            return str(path)
        except Exception as e:
            raise ValueError(f"Invalid repository path: {e}")

    def get_commit_stats(self, commit_hash: str = "HEAD") -> CommitStats:
        """Get statistics for a single commit."""
        # Validate commit hash to prevent injection
        if not self._is_valid_commit_hash(commit_hash):
            raise ValueError("Invalid commit hash format")
            
        # Get commit info
        cmd = [
            "git",
            "-C",
            self.repo_path,
            "show",
            "--format=%H|%an|%ad|%s",
            "--date=iso",
            "--numstat",
            commit_hash,
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=30
        )

        lines = result.stdout.strip().split("\n")
        header = lines[0].split("|")

        commit_hash = header[0]
        author = header[1]
        date = datetime.fromisoformat(header[2].replace(" ", "T"))
        message = header[3]

        files = []
        total_added = 0
        total_deleted = 0

        for line in lines[2:]:  # Skip header and empty line
            if line.strip():
                parts = line.split("\t")
                if len(parts) >= 3:
                    added = int(parts[0]) if parts[0] != "-" else 0
                    deleted = int(parts[1]) if parts[1] != "-" else 0
                    path = parts[2]

                    files.append(
                        FileStats(
                            path=path,
                            lines_added=added,
                            lines_deleted=deleted,
                            lines_changed=added + deleted,
                        )
                    )

                    total_added += added
                    total_deleted += deleted

        return CommitStats(
            hash=commit_hash,
            author=author,
            date=date,
            message=message,
            files_changed=len(files),
            lines_added=total_added,
            lines_deleted=total_deleted,
            files=files,
        )

    def get_range_analytics(
        self, since: str, until: str = "HEAD"
    ) -> RangeStats:
        """Get analytics for a range of commits."""
        # Validate date parameters
        if not self._is_valid_date_string(since):
            raise ValueError("Invalid since date format")
        if not self._is_valid_date_string(until):
            raise ValueError("Invalid until date format")
            
        # Get commit list
        cmd = [
            "git",
            "-C",
            self.repo_path,
            "log",
            f"--since={since}",
            f"--until={until}",
            "--format=%H",
            "--reverse",
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=30
        )

        commit_hashes = [
            line.strip()
            for line in result.stdout.strip().split("\n")
            if line.strip()
        ]

        commits = []
        authors = {}
        total_files = 0
        total_added = 0
        total_deleted = 0

        for commit_hash in commit_hashes:
            try:
                commit_stats = self.get_commit_stats(commit_hash)
                commits.append(commit_stats)

                # Update author stats
                authors[commit_stats.author] = (
                    authors.get(commit_stats.author, 0) + 1
                )

                # Update totals
                total_files += commit_stats.files_changed
                total_added += commit_stats.lines_added
                total_deleted += commit_stats.lines_deleted

            except subprocess.CalledProcessError:
                continue  # Skip problematic commits

        start_date = commits[0].date if commits else datetime.now()
        end_date = commits[-1].date if commits else datetime.now()

        return RangeStats(
            start_date=start_date,
            end_date=end_date,
            total_commits=len(commits),
            total_files_changed=total_files,
            total_lines_added=total_added,
            total_lines_deleted=total_deleted,
            commits=commits,
            authors=authors,
        )

    def _is_valid_commit_hash(self, commit_hash: str) -> bool:
        """Validate commit hash format to prevent injection."""
        import re
        
        # Reject empty or overly long inputs
        if not commit_hash or len(commit_hash) > 100:
            return False
            
        # Allow HEAD, branch names, and valid commit hashes
        if commit_hash in {"HEAD", "HEAD~", "HEAD^"}:
            return True
        # Allow branch names (alphanumeric, hyphens, underscores, slashes, dots)
        if re.match(r'^[a-zA-Z0-9\-_/.]+$', commit_hash):
            return True
        # Allow full commit hashes (40 hex chars)
        if re.match(r'^[a-fA-F0-9]{40}$', commit_hash):
            return True
        # Allow short commit hashes (7-40 hex chars)
        if re.match(r'^[a-fA-F0-9]{7,40}$', commit_hash):
            return True
        return False

    def _is_valid_date_string(self, date_str: str) -> bool:
        """Validate date string format to prevent injection."""
        import re
        
        # Reject empty or overly long inputs
        if not date_str or len(date_str) > 50:
            return False
            
        # Allow relative dates (e.g., "1 week ago", "2 days ago")
        if re.match(r'^\d+\s+(second|minute|hour|day|week|month|year)s?\s+ago$', date_str, re.IGNORECASE):
            return True
        # Allow ISO dates (YYYY-MM-DD)
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return True
        # Allow ISO datetime (YYYY-MM-DD HH:MM:SS)
        if re.match(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}$', date_str):
            return True
        # Allow HEAD
        if date_str == "HEAD":
            return True
        return False
