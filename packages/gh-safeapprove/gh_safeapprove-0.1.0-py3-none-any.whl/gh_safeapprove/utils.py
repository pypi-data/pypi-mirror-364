"""Utility functions for diff parsing and pattern matching."""

import re
import sys
from typing import List


def parse_diff(diff_output: str) -> List[str]:
    """Parse diff output and extract added lines.

    Args:
        diff_output: Raw diff output from gh pr diff

    Returns:
        List of added lines (without the '+' prefix)
    """
    added_lines = []

    for line in diff_output.split("\n"):
        line = line.strip()
        if line.startswith("+") and not line.startswith("+++"):
            # Remove the '+' prefix and add to list
            content = line[1:]
            if content:  # Skip empty lines
                added_lines.append(content)

    return added_lines


def match_pattern(lines: List[str], pattern: str) -> bool:
    """Check if all lines match the given regex pattern.

    Args:
        lines: List of lines to check
        pattern: Regex pattern to match against

    Returns:
        True if all lines match the pattern, False otherwise
    """
    if not lines:
        return False

    try:
        regex = re.compile(pattern)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern '{pattern}': {e}")

    for line in lines:
        if not regex.search(line):
            return False

    return True


def validate_pr_url(url: str) -> bool:
    """Validate that a URL looks like a GitHub pull request URL.

    Args:
        url: URL to validate

    Returns:
        True if URL appears to be a valid GitHub PR URL
    """
    # Basic validation - should contain github (or enterprise host) and /pull/
    return ("github.com" in url or "github." in url) and "/pull/" in url


def extract_pr_urls_from_file(file_path: str) -> List[str]:
    """Extract PR URLs from a file.

    Args:
        file_path: Path to the file containing PR URLs

    Returns:
        List of PR URLs
    """
    urls = []

    try:
        with open(file_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith("#"):  # Skip empty lines and comments
                    if validate_pr_url(line):
                        urls.append(line)
                    else:
                        print(
                            f"Warning: Invalid PR URL on line {line_num}: {line}",
                            file=sys.stderr,
                        )
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")

    return urls


def extract_pr_urls_from_stdin() -> List[str]:
    """Extract PR URLs from stdin.

    Returns:
        List of PR URLs
    """
    urls = []

    try:
        for line in sys.stdin:
            line = line.strip()
            if line and not line.startswith("#"):  # Skip empty lines and comments
                if validate_pr_url(line):
                    urls.append(line)
                else:
                    print(f"Warning: Invalid PR URL: {line}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return []

    return urls
