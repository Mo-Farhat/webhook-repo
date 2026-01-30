
from datetime import datetime, timezone


def normalize_push_event(payload: dict) -> dict:

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

    if gh_event == "push":
        return normalize_push_event(payload)
    elif gh_event == "pull_request":
        return normalize_pr_event(payload)
    else:
        # Unsupported event type
        return None
