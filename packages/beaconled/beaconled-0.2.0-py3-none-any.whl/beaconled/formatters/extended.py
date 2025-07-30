"""Extended output formatter."""

import colorama
from colorama import Fore, Style
from typing import Dict, List
from collections import defaultdict
from datetime import datetime, timedelta

from ..core.models import CommitStats, RangeStats
from .standard import StandardFormatter

# Initialize colorama for cross-platform color support
colorama.init()

class ExtendedFormatter(StandardFormatter):
    """Extended formatter with additional details including author breakdowns and temporal analysis."""

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics with extended details."""
        output = super().format_commit_stats(stats)

        if stats.files:
            # Add file type analysis
            file_types = {}
            for file_stat in stats.files:
                ext = (
                    file_stat.path.split(".")[-1]
                    if "." in file_stat.path
                    else "no-ext"
                )
                if ext not in file_types:
                    file_types[ext] = {
                        "count": 0,
                        "added": 0,
                        "deleted": 0,
                    }
                file_types[ext]["count"] += 1
                file_types[ext]["added"] += file_stat.lines_added
                file_types[ext]["deleted"] += file_stat.lines_deleted

            output += f"\n\n{Fore.MAGENTA}File type breakdown:{Style.RESET_ALL}"
            for ext, data in sorted(file_types.items()):
                output += (
                    f"\n  .{Fore.CYAN}{ext}{Style.RESET_ALL}: "
                    f"{data['count']} files, "
                    f"{Fore.GREEN}+{data['added']}{Style.RESET_ALL} "
                    f"{Fore.RED}-{data['deleted']}{Style.RESET_ALL}"
                )

        return output

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics with extended details including author breakdowns and temporal analysis."""
        output = super().format_range_stats(stats)
        
        # Add author contribution breakdown
        if stats.authors:
            output += f"\n\n{Fore.MAGENTA}Author Contribution Breakdown:{Style.RESET_ALL}"
            total_commits = stats.total_commits
            for author, count in sorted(stats.authors.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_commits) * 100
                output += f"\n  {Fore.CYAN}{author}{Style.RESET_ALL}: {count} commits ({percentage:.1f}%)"
        
        # Add temporal analysis visualization
        if stats.commits:
            # Daily activity timeline
            daily_activity = defaultdict(int)
            for commit in stats.commits:
                day = commit.date.strftime("%Y-%m-%d")
                daily_activity[day] += 1
            
            # Get date range
            start_date = min(commit.date for commit in stats.commits)
            end_date = max(commit.date for commit in stats.commits)
            
            # Create timeline visualization
            output += f"\n\n{Fore.MAGENTA}Temporal Analysis - Daily Activity Timeline:{Style.RESET_ALL}"
            current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date_trunc = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            while current_date <= end_date_trunc:
                date_str = current_date.strftime("%Y-%m-%d")
                commit_count = daily_activity[date_str]
                bar = "█" * min(commit_count, 50)  # Limit bar length to 50 characters
                output += f"\n  {Fore.CYAN}{date_str}{Style.RESET_ALL}: {commit_count:2d} {bar}"
                current_date += timedelta(days=1)
        
        return output
