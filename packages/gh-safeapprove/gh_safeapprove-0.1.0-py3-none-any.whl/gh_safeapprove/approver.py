"""Main approval logic for gh-safeapprove."""

import sys
from typing import List, Optional

from .github_client import GitHubClient
from .utils import parse_diff, match_pattern


class Approver:
    """Main class for handling PR approval logic."""

    def __init__(self, enterprise_host: Optional[str] = None):
        """Initialize the approver.

        Args:
            enterprise_host: Optional GitHub Enterprise hostname
        """
        self.github_client = GitHubClient(enterprise_host)

    def check_pr_approval(
        self, pr_url: str, pattern: str, dry_run: bool = False
    ) -> bool:
        """Check if a PR should be approved based on the given pattern.

        Args:
            pr_url: URL of the pull request
            pattern: Regex pattern to match against added lines
            dry_run: If True, don't actually approve, just show what would happen

        Returns:
            True if PR was approved or would be approved (in dry run), False otherwise
        """
        print(f"Processing PR: {pr_url}")

        # Get the diff for the PR
        return_code, diff_output, stderr = self.github_client.get_pr_diff(pr_url)

        if return_code != 0:
            print(f"Error getting diff for {pr_url}: {stderr}", file=sys.stderr)
            return False

        # Parse the diff to get added lines
        added_lines = parse_diff(diff_output)

        if not added_lines:
            print(f"No added lines found in PR {pr_url}")
            return False

        print(f"Found {len(added_lines)} added lines")

        # Check if all added lines match the pattern
        try:
            matches = match_pattern(added_lines, pattern)
        except ValueError as e:
            print(f"Error with regex pattern: {e}", file=sys.stderr)
            return False

        if matches:
            print(f"✓ All added lines match pattern '{pattern}'")

            if dry_run:
                print(f"DRY RUN: Would approve PR {pr_url}")
                return True
            else:
                # Actually approve the PR
                return_code, _, stderr = self.github_client.approve_pr(pr_url)

                if return_code == 0:
                    print(f"✓ Approved PR {pr_url}")
                    return True
                else:
                    print(f"Error approving PR {pr_url}: {stderr}", file=sys.stderr)
                    return False
        else:
            print(f"✗ Not all added lines match pattern '{pattern}'")
            return False

    def process_prs(
        self, pr_urls: List[str], pattern: str, dry_run: bool = False
    ) -> List[bool]:
        """Process multiple PRs and return approval results.

        Args:
            pr_urls: List of PR URLs to process
            pattern: Regex pattern to match against added lines
            dry_run: If True, don't actually approve, just show what would happen

        Returns:
            List of boolean results indicating success/failure for each PR
        """
        results = []

        for pr_url in pr_urls:
            result = self.check_pr_approval(pr_url, pattern, dry_run)
            results.append(result)
            print()  # Add spacing between PRs

        return results

    def check_auth(self) -> bool:
        """Check if the user is authenticated with GitHub.

        Returns:
            True if authenticated, False otherwise
        """
        return self.github_client.check_auth()
