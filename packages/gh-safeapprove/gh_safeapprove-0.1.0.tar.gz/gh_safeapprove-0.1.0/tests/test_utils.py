"""Tests for utility functions."""

import pytest

from gh_safeapprove.utils import (
    parse_diff,
    match_pattern,
    validate_pr_url,
    extract_pr_urls_from_file,
)


class TestParseDiff:
    """Test diff parsing functionality."""

    def test_parse_diff_with_added_lines(self):
        """Test parsing diff with added lines."""
        diff_output = """
diff --git a/file.txt b/file.txt
index 1234567..abcdefg 100644
--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,4 @@
 line1
+new line
 line2
+another new line
 line3
"""
        result = parse_diff(diff_output)
        assert result == ["new line", "another new line"]

    def test_parse_diff_no_added_lines(self):
        """Test parsing diff with no added lines."""
        diff_output = """
diff --git a/file.txt b/file.txt
index 1234567..abcdefg 100644
--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,3 @@
 line1
-line2
+line2 modified
 line3
"""
        result = parse_diff(diff_output)
        assert result == ["line2 modified"]

    def test_parse_diff_empty(self):
        """Test parsing empty diff."""
        result = parse_diff("")
        assert result == []

    def test_parse_diff_ignores_headers(self):
        """Test that diff headers are ignored."""
        diff_output = """
diff --git a/file.txt b/file.txt
index 1234567..abcdefg 100644
--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,4 @@
 line1
+new line
 line2
 line3
"""
        result = parse_diff(diff_output)
        assert result == ["new line"]


class TestMatchPattern:
    """Test pattern matching functionality."""

    def test_match_pattern_simple(self):
        """Test simple pattern matching."""
        lines = ["hello world", "hello there"]
        assert match_pattern(lines, r"hello") is True

    def test_match_pattern_complex(self):
        """Test complex regex pattern."""
        lines = ["url = 'https://example.com'", "url = 'https://test.com'"]
        assert match_pattern(lines, r"url\s*=") is True

    def test_match_pattern_partial_match(self):
        """Test when not all lines match."""
        lines = ["hello world", "goodbye world"]
        assert match_pattern(lines, r"hello") is False

    def test_match_pattern_empty_lines(self):
        """Test with empty lines."""
        assert match_pattern([], r"hello") is False

    def test_match_pattern_invalid_regex(self):
        """Test with invalid regex pattern."""
        with pytest.raises(ValueError):
            match_pattern(["hello"], r"[invalid")


class TestValidatePrUrl:
    """Test PR URL validation."""

    def test_valid_pr_url(self):
        """Test valid PR URL."""
        url = "https://github.com/owner/repo/pull/123"
        assert validate_pr_url(url) is True

    def test_invalid_pr_url(self):
        """Test invalid PR URL."""
        url = "https://github.com/owner/repo/issues/123"
        assert validate_pr_url(url) is False

    def test_non_github_url(self):
        """Test non-GitHub URL."""
        url = "https://gitlab.com/owner/repo/merge_requests/123"
        assert validate_pr_url(url) is False


class TestExtractPrUrlsFromFile:
    """Test extracting PR URLs from file."""

    def test_extract_valid_urls(self, tmp_path):
        """Test extracting valid PR URLs."""
        file_content = """
https://github.com/owner/repo/pull/123
# This is a comment
https://github.com/owner/repo/pull/456
https://github.com/owner/repo/pull/789
"""
        file_path = tmp_path / "prs.txt"
        file_path.write_text(file_content)

        result = extract_pr_urls_from_file(str(file_path))
        assert result == [
            "https://github.com/owner/repo/pull/123",
            "https://github.com/owner/repo/pull/456",
            "https://github.com/owner/repo/pull/789",
        ]

    def test_extract_with_invalid_urls(self, tmp_path):
        """Test extracting with some invalid URLs."""
        file_content = """
https://github.com/owner/repo/pull/123
https://github.com/owner/repo/issues/456
https://github.com/owner/repo/pull/789
"""
        file_path = tmp_path / "prs.txt"
        file_path.write_text(file_content)

        result = extract_pr_urls_from_file(str(file_path))
        assert result == [
            "https://github.com/owner/repo/pull/123",
            "https://github.com/owner/repo/pull/789",
        ]

    def test_file_not_found(self):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            extract_pr_urls_from_file("nonexistent.txt")
