"""
GitHub Webhook Receiver

A Flask application that receives GitHub webhook events (push, pull_request),
normalizes them, stores them in MongoDB, and serves a UI to display events.

Endpoints:
    GET  /           - Serves the frontend UI
    POST /webhook    - Receives GitHub webhook payloads
    GET  /events     - Returns stored events as JSON (supports incremental fetching)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient, DESCENDING
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from models import normalize_event

app = Flask(__name__, static_folder="../frontend")
CORS(app)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
events = db[COLLECTION_NAME]


@app.get("/")
def home():
    """
    Serve the frontend single-page application.

    Returns:
        The index.html file from the frontend directory.
    """
    return send_from_directory(app.static_folder, "index.html")


@app.get("/<path:filename>")
def serve_static(filename):
    """
    Serve static files (JS, CSS) from the frontend directory.

    Args:
        filename: The requested file path.

    Returns:
        The requested static file.
    """
    return send_from_directory(app.static_folder, filename)


@app.post("/webhook")
def webhook():
    """
    Receive and process GitHub webhook events.

    Expected headers:
        X-GitHub-Event: The type of GitHub event (push, pull_request, etc.)

    Expected body:
        JSON payload from GitHub webhook.

    Supported events:
        - push: Records when code is pushed to a branch
        - pull_request: Records PR creation, updates, and merges

    Returns:
        JSON response with status.
    """
    # GitHub sends event type in X-GitHub-Event header
    gh_event = request.headers.get("X-GitHub-Event", "unknown")
    payload = request.get_json(silent=True) or {}

    # Normalize the event using our models
    doc = normalize_event(gh_event, payload)

    if doc is None:
        # Unsupported event type - acknowledge but don't store
        return jsonify({"ok": True, "message": f"Event type '{gh_event}' ignored"})

    # Store in MongoDB
    events.insert_one(doc)

    return jsonify({"ok": True, "action": doc["action"]})


@app.get("/events")
def get_events():
    """
    Retrieve stored events, optionally filtered by timestamp.

    Query parameters:
        limit (int): Maximum number of events to return (default: 20)
        since (str): ISO timestamp - only return events after this time

    Returns:
        JSON array of event objects, sorted by timestamp descending.
    """
    limit = int(request.args.get("limit", 20))
    since = request.args.get("since")

    # Build query filter
    query = {}
    if since:
        # Only return events newer than the 'since' timestamp
        query["timestamp"] = {"$gt": since}

    cursor = events.find(query, {"_id": 0}).sort("timestamp", DESCENDING).limit(limit)
    return jsonify(list(cursor))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
