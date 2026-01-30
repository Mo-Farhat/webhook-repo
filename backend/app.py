
import utils.transport
import utils.session
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
    return send_from_directory(app.static_folder, "index.html")


@app.get("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


@app.post("/webhook")
def webhook():

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
