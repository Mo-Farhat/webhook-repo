You are helping me implement a coding assignment:

Goal:
Build a GitHub webhook tracker using two repositories:

1. action-repo: a GitHub repo configured with GitHub Webhooks to send events on Push and Pull Request (optional Merge).
2. webhook-repo: a Flask application that receives GitHub webhooks, stores normalized events in MongoDB, and serves a minimal UI that polls every 15 seconds and displays the latest events.

Required UI formats:
PUSH: "{author} pushed to {to_branch} on {timestamp}"
PULL_REQUEST: "{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
MERGE (bonus): "{author} merged branch {from_branch} to {to_branch} on {timestamp}"

MongoDB schema (events collection):

- request_id: string (push: commit hash, PR: PR id)
- author: string
- action: enum string "PUSH" | "PULL_REQUEST" | "MERGE"
- from_branch: string
- to_branch: string
- timestamp: UTC datetime string

Key constraints:

- Flask webhook endpoint must be clean, readable, and well-documented.
- Date handling must be correct; store and display in UTC.
- UI polls every 15 seconds but must NOT re-display duplicates outside the refresh window; implement incremental fetching (e.g., /events?since=... or last_seen_id).
- Provide endpoints: POST /webhook, GET /events (JSON), and a simple frontend that renders the formatted strings.

Deliverables:

- Two GitHub repos (action-repo + webhook-repo) and a demo walkthrough video link.
