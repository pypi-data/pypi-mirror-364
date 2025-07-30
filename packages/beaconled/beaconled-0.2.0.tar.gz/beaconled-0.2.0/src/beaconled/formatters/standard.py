"""Standard output formatter."""

import colorama
from colorama import Fore, Style

from ..core.models import CommitStats, RangeStats

# Initialize colorama for cross-platform color support
colorama.init()

class StandardFormatter:
    """Standard text formatter for Beacon delivery analytics output."""

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics as standard text."""
        output = []
        output.append(f"{Fore.CYAN}Commit:{Style.RESET_ALL} {stats.hash[:8]}")
        output.append(f"{Fore.CYAN}Author:{Style.RESET_ALL} {stats.author}")
        output.append(f"{Fore.CYAN}Date:{Style.RESET_ALL} {stats.date.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"{Fore.CYAN}Message:{Style.RESET_ALL} {stats.message}")
        output.append("")
        output.append(f"{Fore.YELLOW}Files changed:{Style.RESET_ALL} {stats.files_changed}")
        output.append(f"{Fore.GREEN}Lines added:{Style.RESET_ALL} {stats.lines_added}")
        output.append(f"{Fore.RED}Lines deleted:{Style.RESET_ALL} {stats.lines_deleted}")
        
        net_change = stats.lines_added - stats.lines_deleted
        net_color = Fore.GREEN if net_change >= 0 else Fore.RED
        output.append(f"{Fore.YELLOW}Net change:{Style.RESET_ALL} {net_color}{net_change}{Style.RESET_ALL}")

        if stats.files:
            output.append("")
            output.append(f"{Fore.MAGENTA}File changes:{Style.RESET_ALL}")
            for file_stat in stats.files:
                output.append(
                    f"  {file_stat.path}: "
                    f"{Fore.GREEN}+{file_stat.lines_added}{Style.RESET_ALL} "
                    f"{Fore.RED}-{file_stat.lines_deleted}{Style.RESET_ALL}"
                )

        return "\n".join(output)

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics as standard text."""
        output = []
        output.append(
            f"{Fore.CYAN}Range Analysis:{Style.RESET_ALL} {stats.start_date.strftime('%Y-%m-%d')} to "
            f"{stats.end_date.strftime('%Y-%m-%d')}"
        )
        output.append("")
        output.append(f"{Fore.YELLOW}Total commits:{Style.RESET_ALL} {stats.total_commits}")
        output.append(f"{Fore.YELLOW}Total files changed:{Style.RESET_ALL} {stats.total_files_changed}")
        output.append(f"{Fore.GREEN}Total lines added:{Style.RESET_ALL} {stats.total_lines_added}")
        output.append(f"{Fore.RED}Total lines deleted:{Style.RESET_ALL} {stats.total_lines_deleted}")
        
        net_change = stats.total_lines_added - stats.total_lines_deleted
        net_color = Fore.GREEN if net_change >= 0 else Fore.RED
        output.append(f"{Fore.YELLOW}Net change:{Style.RESET_ALL} {net_color}{net_change}{Style.RESET_ALL}")

        if stats.authors:
            output.append("")
            output.append(f"{Fore.MAGENTA}Contributors:{Style.RESET_ALL}")
            for author, count in sorted(
                stats.authors.items(), key=lambda x: x[1], reverse=True
            ):
                output.append(f"  {author}: {count} commits")

        return "\n".join(output)
