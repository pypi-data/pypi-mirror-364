# gh-safeapprove

A GitHub CLI-compatible Python tool to **safely auto-approve pull requests** based on customizable rules.

## 🧩 What is `gh-safeapprove`?

`gh-safeapprove` is a CLI tool designed to automate the approval of pull requests, but **only when they meet strict
safety criteria** — such as matching a specific diff pattern, modifying only certain files, or passing a custom rule
check.

It is ideal for teams who want to streamline the review of low-risk, repetitive changes (e.g., version bumps, URL
rewrites, comment-only diffs) without compromising code quality.

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- GitHub CLI (`gh`) installed and authenticated

### Install from PyPI

```bash
pip install gh-safeapprove
```

### Install from source

```bash
# Clone the repository
git clone https://github.com/danielmeint/gh-safeapprove.git
cd gh-safeapprove

# Install in development mode
pip install -e .
```

## 🛠️ Basic Usage

### Phase 1 Features

Currently supports:

- Reading PR URLs from a file or stdin
- Pattern matching on added lines using regex
- Dry-run mode for testing
- GitHub Enterprise support
- Basic authentication checks

```bash
# Approve all PRs listed in a file if their diffs only match the pattern
gh-safeapprove --file prs.txt --pattern '\\.url\\s*=' --dry-run

# Same via stdin
cat prs.txt | gh-safeapprove --stdin --pattern '\\.url\\s*='

# Using GitHub Enterprise instance
gh-safeapprove --file prs.txt --enterprise-host github.enterprise.com
```

### Input Format

Create a file with PR URLs (one per line):

```text
https://github.com/owner/repo/pull/123
https://github.com/owner/repo/pull/456
# Comments are ignored
https://github.com/owner/repo/pull/789
```

## 📋 Command Line Options

| Option              | Description                                        |
|---------------------|----------------------------------------------------|
| `--file`, `-f`      | File containing PR URLs (one per line)             |
| `--stdin`           | Read PR URLs from stdin                            |
| `--pattern`, `-p`   | Regex pattern to match against added lines         |
| `--dry-run`         | Show what would be done without actually approving |
| `--enterprise-host` | GitHub Enterprise hostname                         |
| `--verbose`, `-v`   | Enable verbose output                              |

## 🔧 Development

### Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/
```

### Project Structure

```
gh-safeapprove/
├── src/
│   └── gh_safeapprove/
│       ├── __init__.py
│       ├── cli.py             # CLI entry point (typer)
│       ├── approver.py        # Main approval logic
│       ├── github_client.py   # Wrapper for `gh` CLI
│       └── utils.py           # Utility functions
├── tests/
├── pyproject.toml
└── README.md
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gh_safeapprove
```

## 📝 License

MIT License - see LICENSE file for details.

## 🚧 Status

**Phase 1 Complete**: Basic functionality with pattern matching and GitHub CLI integration.

Planned for future phases:

- Advanced rule system
- File-scope rules
- GitHub API support
- GitHub Actions integration 
