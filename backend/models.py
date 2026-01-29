"""
GitHub Webhook Event Normalizers

This module provides functions to normalize GitHub webhook payloads
into a consistent schema for storage in MongoDB.
"""

from datetime import datetime, timezone


def normalize_push_event(payload: dict) -> dict:
    """
    Normalize a GitHub 'push' event payload.

    Args:
        payload: The raw GitHub webhook payload for a push event.

    Returns:
        A normalized event dictionary with the following fields:
        - request_id: The commit SHA (after)
        - author: The pusher's name
        - action: "PUSH"
        - from_branch: Empty string (not applicable for push)
        - to_branch: The branch pushed to
        - timestamp: UTC ISO timestamp
    """
    # Extract branch from ref (e.g., "refs/heads/main" -> "main")
    ref = payload.get("ref", "")
    to_branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref

    return {
        "request_id": payload.get("after", ""),
        "author": (payload.get("pusher") or {}).get("name", "unknown"),
        "action": "PUSH",
        "from_branch": "",
        "to_branch": to_branch,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def normalize_pr_event(payload: dict) -> dict:
    """
    Normalize a GitHub 'pull_request' event payload.

    Handles both regular PR events and merged PRs. A PR is considered
    merged when action is 'closed' and pull_request.merged is True.

    Args:
        payload: The raw GitHub webhook payload for a pull_request event.

    Returns:
        A normalized event dictionary with the following fields:
        - request_id: The PR number as string
        - author: The sender's login
        - action: "PULL_REQUEST" or "MERGE"
        - from_branch: The source branch (head)
        - to_branch: The target branch (base)
        - timestamp: UTC ISO timestamp
    """
    pr = payload.get("pull_request") or {}
    action = payload.get("action", "")

    # Determine if this is a merge event
    is_merge = action == "closed" and pr.get("merged", False)

    return {
        "request_id": str(payload.get("number", "")),
        "author": (payload.get("sender") or {}).get("login", "unknown"),
        "action": "MERGE" if is_merge else "PULL_REQUEST",
        "from_branch": (pr.get("head") or {}).get("ref", ""),
        "to_branch": (pr.get("base") or {}).get("ref", ""),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def normalize_event(gh_event: str, payload: dict) -> dict | None:
    """
    Route the payload to the appropriate normalizer based on event type.

    Args:
        gh_event: The X-GitHub-Event header value
        payload: The raw GitHub webhook payload

    Returns:
        A normalized event dictionary, or None if event type is unsupported.
    """
    if gh_event == "push":
        return normalize_push_event(payload)
    elif gh_event == "pull_request":
        return normalize_pr_event(payload)
    else:
        # Unsupported event type
        return None
