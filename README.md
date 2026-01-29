# GitHub Webhook Tracker

A Flask application that receives GitHub webhook events, stores them in MongoDB, and displays them in a real-time UI that polls every 15 seconds.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────┐
│   GitHub Repo   │─────▶│   Flask Server   │─────▶│   MongoDB   │
│  (action-repo)  │      │  (webhook-repo)  │      │   (events)  │
└─────────────────┘      └──────────────────┘      └─────────────┘
      Webhooks                   │
                                 ▼
                         ┌──────────────────┐
                         │   Frontend UI    │
                         │  (polls /events) │
                         └──────────────────┘
```

## Features

- **Webhook Processing**: Receives GitHub `push` and `pull_request` events
- **MERGE Detection**: Automatically detects when a PR is merged
- **Incremental Fetching**: UI only fetches new events to avoid duplicates
- **Real-time Updates**: Auto-refreshes every 15 seconds
- **Modern UI**: Dark theme with action-specific color coding

## Event Formats

| Event        | Display Format                                                                       |
| ------------ | ------------------------------------------------------------------------------------ |
| PUSH         | `{author} pushed to {to_branch} on {timestamp}`                                      |
| PULL_REQUEST | `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}` |
| MERGE        | `{author} merged branch {from_branch} to {to_branch} on {timestamp}`                 |

## Prerequisites

- Python 3.10+
- MongoDB (local or Atlas)

## Quick Start

### 1. Clone and Setup

```bash
cd webhook-repo/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `backend/.env`:

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=github_events
COLLECTION_NAME=events
```

### 3. Start MongoDB

```bash
# Local MongoDB
mongod

# Or use Docker
docker run -d -p 27017:27017 mongo
```

### 4. Run the Server

```bash
cd backend
python app.py
```

Open http://localhost:5000 to view the UI.

## API Endpoints

### `POST /webhook`

Receives GitHub webhook payloads.

**Headers:**

- `X-GitHub-Event`: Event type (`push`, `pull_request`)
- `Content-Type`: `application/json`

**Response:**

```json
{ "ok": true, "action": "PUSH" }
```

### `GET /events`

Returns stored events.

**Query Parameters:**

- `limit` (optional): Max events to return (default: 20)
- `since` (optional): ISO timestamp for incremental fetching

**Response:**

```json
[
  {
    "request_id": "abc123",
    "author": "username",
    "action": "PUSH",
    "from_branch": "",
    "to_branch": "main",
    "timestamp": "2026-01-29T16:30:00+00:00"
  }
]
```

## MongoDB Schema

Collection: `events`

| Field         | Type   | Description                        |
| ------------- | ------ | ---------------------------------- |
| `request_id`  | string | Commit SHA (push) or PR number     |
| `author`      | string | Username who triggered the event   |
| `action`      | string | `PUSH`, `PULL_REQUEST`, or `MERGE` |
| `from_branch` | string | Source branch (PRs only)           |
| `to_branch`   | string | Target branch                      |
| `timestamp`   | string | UTC ISO 8601 timestamp             |

## Configure GitHub Webhook

1. Go to your **action-repo** on GitHub
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-server.com/webhook`
   - **Content type**: `application/json`
   - **Events**: Select `Push` and `Pull requests`
4. Click **Add webhook**

## Testing Locally

Use `ngrok` or similar to expose your local server:

```bash
ngrok http 5000
```

Then use the generated URL as your webhook payload URL.

### Test with cURL

```bash
# Test PUSH event
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{"ref":"refs/heads/main","after":"abc123","pusher":{"name":"testuser"}}'

# Test PULL_REQUEST event
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -d '{"action":"opened","number":42,"pull_request":{"head":{"ref":"feature"},"base":{"ref":"main"}},"sender":{"login":"testuser"}}'

# Test MERGE event
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -d '{"action":"closed","number":42,"pull_request":{"head":{"ref":"feature"},"base":{"ref":"main"},"merged":true},"sender":{"login":"testuser"}}'
```

## Project Structure

```
webhook-repo/
├── backend/
│   ├── app.py          # Flask application
│   ├── models.py       # Event normalization logic
│   ├── config.py       # Environment configuration
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html      # Main HTML page
│   ├── app.js          # Frontend logic (polling, rendering)
│   └── styles.css      # Modern dark theme styles
└── README.md
```

## License

MIT
