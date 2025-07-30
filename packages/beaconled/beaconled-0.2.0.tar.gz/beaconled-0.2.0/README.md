# Beacon

Your delivery compass for empowered product builders.

A comprehensive toolkit for analyzing git repository statistics and development metrics.

## Features

- Commit-level analytics with detailed breakdowns
- Component and file type analysis
- Impact assessment (high/medium/low)
- Range analysis for teams and sprints
- Multiple output formats (standard, extended, JSON)
- Integration with CI/CD pipelines and git hooks

## Installation

Beacon requires Python 3.7+ and Git. We recommend installing in a virtual environment.

### Quick Install

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install from PyPI
pip install beaconled
```

### Verify Installation

```bash
beaconled --version
```

For more detailed instructions, including development setup and troubleshooting, see the [Installation Guide](docs/installation.md).

## Quick Start

Analyze a git repository:

```bash
beaconled /path/to/repo
```

Generate a weekly team report:
```bash
beaconled --range --since "1 week ago"
```

For more detailed usage examples, please refer to the [Usage Examples](docs/usage.md).

## Sample Outputs

### Analyzing a Git Repository

When analyzing a repository, Beacon provides commit details, file changes, and metrics in the standard format:

```bash
beaconled /path/to/my-project
```

```bash
Repository Analysis: /path/to/my-project
Analysis Period: Last 30 commits

=== COMMIT SUMMARY ===
Total Commits: 30
Contributors: 4
Date Range: 2025-01-15 to 2025-01-23

=== COMMIT DETAILS ===
[2025-01-23 14:32] feat: Add user authentication module (John Doe)
  Impact: HIGH - 8 files changed, 245 insertions, 12 deletions
  Components: auth/, middleware/, tests/
  
[2025-01-23 10:15] fix: Resolve database connection timeout (Jane Smith)
  Impact: MEDIUM - 3 files changed, 28 insertions, 15 deletions
  Components: database/, config/
  
[2025-01-22 16:45] docs: Update API documentation (Mike Johnson)
  Impact: LOW - 2 files changed, 67 insertions, 3 deletions
  Components: docs/

=== FILE CHANGE METRICS ===
Most Active Files:
  src/auth/login.py: 12 changes
  config/database.py: 8 changes
  tests/test_auth.py: 6 changes

File Type Breakdown:
  Python (.py): 18 files, 456 lines changed
  Markdown (.md): 4 files, 89 lines changed
  JSON (.json): 2 files, 23 lines changed

=== IMPACT ASSESSMENT ===
High Impact Commits: 8 (27%)
Medium Impact Commits: 15 (50%)
Low Impact Commits: 7 (23%)
```

### Generating Weekly Team Reports

For range analysis with contributor breakdown and commit frequency:

```bash
beaconled --range --since "1 week ago" --format standard
```

```bash
Weekly Team Report
Analysis Period: 2025-01-16 to 2025-01-23 (7 days)

=== TEAM OVERVIEW ===
Total Contributors: 4
Total Commits: 23
Average Commits/Day: 3.3
Active Days: 6/7

=== CONTRIBUTOR BREAKDOWN ===
John Doe: 9 commits (39%)
  - High Impact: 3 commits
  - Medium Impact: 4 commits  
  - Low Impact: 2 commits
  - Most Active: Monday, Wednesday

Jane Smith: 7 commits (30%)
  - High Impact: 2 commits
  - Medium Impact: 3 commits
  - Low Impact: 2 commits
  - Most Active: Tuesday, Thursday

Mike Johnson: 4 commits (17%)
  - High Impact: 1 commit
  - Medium Impact: 2 commits
  - Low Impact: 1 commit
  - Most Active: Friday

Sarah Wilson: 3 commits (13%)
  - High Impact: 0 commits
  - Medium Impact: 2 commits
  - Low Impact: 1 commit
  - Most Active: Monday

=== COMMIT FREQUENCY ===
Monday: 5 commits (22%)
Tuesday: 4 commits (17%)
Wednesday: 6 commits (26%)
Thursday: 3 commits (13%)
Friday: 3 commits (13%)
Saturday: 1 commit (4%)
Sunday: 1 commit (4%)

=== COMPONENT ACTIVITY ===
Most Changed Components:
  frontend/: 8 commits, 234 lines
  backend/api/: 6 commits, 189 lines
  tests/: 5 commits, 156 lines
  docs/: 4 commits, 78 lines
```

## Documentation

- [Installation Guide](https://github.com/shrwnsan/beacon-delivery-compass/blob/main/docs/installation.md)
- [Usage Examples](https://github.com/shrwnsan/beacon-delivery-compass/blob/main/docs/usage.md)
- [Integration Guide](https://github.com/shrwnsan/beacon-delivery-compass/blob/main/docs/integrations.md)
- [API Reference](https://github.com/shrwnsan/beacon-delivery-compass/blob/main/docs/api-reference.md)
- [Changelog](https://github.com/shrwnsan/beacon-delivery-compass/blob/main/CHANGELOG.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
