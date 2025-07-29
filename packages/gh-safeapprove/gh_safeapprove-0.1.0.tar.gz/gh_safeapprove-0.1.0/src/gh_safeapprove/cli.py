"""CLI entry point for gh-safeapprove."""

from typing import Optional

import typer

from .approver import Approver
from .utils import extract_pr_urls_from_file, extract_pr_urls_from_stdin

app = typer.Typer(
    name="gh-safeapprove",
    help="Safely auto-approve pull requests based on customizable rules",
    add_completion=False,
)


@app.command()
def main(
    file: Optional[str] = typer.Option(
        None, "--file", "-f", help="File containing PR URLs (one per line)"
    ),
    stdin: bool = typer.Option(False, "--stdin", help="Read PR URLs from stdin"),
    pattern: str = typer.Option(
        ..., "--pattern", "-p", help="Regex pattern to match against added lines"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without actually approving"
    ),
    enterprise_host: Optional[str] = typer.Option(
        None, "--enterprise-host", help="GitHub Enterprise hostname"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """Safely auto-approve pull requests based on customizable rules."""

    # Validate input options
    if not file and not stdin:
        typer.echo("Error: Must specify either --file or --stdin", err=True)
        raise typer.Exit(1)

    if file and stdin:
        typer.echo("Error: Cannot specify both --file and --stdin", err=True)
        raise typer.Exit(1)

    # Initialize the approver
    approver = Approver(enterprise_host)

    # Check authentication
    if not approver.check_auth():
        typer.echo(
            "Error: Not authenticated with GitHub. Run 'gh auth login' first.", err=True
        )
        raise typer.Exit(1)

    # Get PR URLs
    try:
        if file:
            pr_urls = extract_pr_urls_from_file(file)
        else:
            pr_urls = extract_pr_urls_from_stdin()
    except (FileNotFoundError, Exception) as e:
        typer.echo(f"Error reading PR URLs: {e}", err=True)
        raise typer.Exit(1)

    if not pr_urls:
        typer.echo("No valid PR URLs found", err=True)
        raise typer.Exit(1)

    if verbose:
        typer.echo(f"Found {len(pr_urls)} PR URLs to process")

    # Process PRs
    results = approver.process_prs(pr_urls, pattern, dry_run)

    # Summary
    successful = sum(results)
    total = len(results)

    if dry_run:
        typer.echo(f"\nDRY RUN SUMMARY: {successful}/{total} PRs would be approved")
    else:
        typer.echo(f"\nSUMMARY: {successful}/{total} PRs approved")

    # Exit with error code if any PRs failed
    if successful < total:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
