"""GitHub CLI wrapper for running gh commands via subprocess."""

import os
import subprocess
import sys
from typing import List, Optional, Tuple


class GitHubClient:
    """Wrapper for GitHub CLI commands using subprocess."""

    def __init__(self, enterprise_host: Optional[str] = None):
        """Initialize the GitHub client.

        Args:
            enterprise_host: Optional GitHub Enterprise hostname
        """
        self.enterprise_host = enterprise_host

    def _run_gh_command(
        self, args: List[str], capture_output: bool = True
    ) -> Tuple[int, str, str]:
        """Run a gh command and return the result.

        Args:
            args: List of arguments to pass to gh
            capture_output: Whether to capture stdout/stderr

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = ["gh"] + args

        # Set GH_HOST if enterprise host is specified
        env = None
        if self.enterprise_host:
            env = dict(os.environ)
            env["GH_HOST"] = self.enterprise_host

        try:
            result = subprocess.run(
                cmd, capture_output=capture_output, text=True, env=env, check=False
            )
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError:
            print(
                "Error: GitHub CLI (gh) is not installed or not in PATH",
                file=sys.stderr,
            )
            return 1, "", "GitHub CLI (gh) is not installed or not in PATH"

    def get_pr_diff(self, pr_url: str) -> Tuple[int, str, str]:
        """Get the diff for a pull request.

        Args:
            pr_url: URL of the pull request

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        return self._run_gh_command(["pr", "diff", pr_url])

    def approve_pr(self, pr_url: str) -> Tuple[int, str, str]:
        """Approve a pull request.

        Args:
            pr_url: URL of the pull request

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        return self._run_gh_command(["pr", "review", "--approve", pr_url])

    def check_auth(self) -> bool:
        """Check if the user is authenticated with GitHub.

        Returns:
            True if authenticated, False otherwise
        """
        return_code, _, _ = self._run_gh_command(["auth", "status"])
        return return_code == 0
