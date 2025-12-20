#!/usr/bin/env python3
"""Git security hook for validating remote URLs."""

import re
from typing import List


def is_anthropics_url(url: str) -> bool:
    """
    Check if a git remote URL belongs to the Anthropics organization.

    Args:
        url: Git remote URL to check

    Returns:
        bool: True if the URL belongs to Anthropics org, False otherwise
    """
    # Check for anthropics org in various URL formats
    patterns = [
        r"github\.com[/:]anthropics/",  # Matches both HTTPS and SSH
        r"^anthropics/",  # Direct org/repo format
        r"git-proxy\.infra[/:]anthropics/",  # Git proxy for devspace, matches both HTTPS and SSH
    ]

    for pattern in patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True

    return False


def validate_git_remotes(remotes: List[str]) -> List[str]:
    """
    Validate a list of git remote URLs.

    Args:
        remotes: List of git remote URLs to validate

    Returns:
        List[str]: List of invalid remote URLs
    """
    invalid_remotes = []

    for remote in remotes:
        if not is_anthropics_url(remote):
            invalid_remotes.append(remote)

    return invalid_remotes


if __name__ == "__main__":
    # Test cases
    test_urls = [
        "https://github.com/anthropics/some-repo.git",
        "git@github.com:anthropics/some-repo.git",
        "anthropics/some-repo",
        "https://git-proxy.infra/anthropics/some-repo.git",
        "git@git-proxy.infra:anthropics/some-repo.git",
        "https://github.com/other-org/some-repo.git",
        "git@github.com:other-org/some-repo.git",
    ]

    print("Testing is_anthropics_url function:")
    for url in test_urls:
        result = is_anthropics_url(url)
        print(f"  {url}: {'✓' if result else '✗'}")