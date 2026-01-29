/**
 * GitHub Events Feed - Frontend Application
 *
 * Polls the /events endpoint every 15 seconds and displays
 * formatted event messages. Uses incremental fetching to
 * avoid re-displaying duplicate events.
 */

const feed = document.getElementById("feed");
const statusEl = document.getElementById("status");
const countEl = document.getElementById("count");

// Track the most recent event timestamp for incremental fetching
let lastSeenTimestamp = null;

// Track seen event IDs to prevent any duplicates
const seenEventIds = new Set();

/**
 * Format an event object into a human-readable string.
 * @param {Object} e - The event object
 * @returns {string} Formatted event message
 */
function formatEvent(e) {
  const time = new Date(e.timestamp).toLocaleString();

  if (e.action === "PUSH") {
    return `${e.author} pushed to ${e.to_branch || "unknown"} on ${time}`;
  }
  if (e.action === "PULL_REQUEST") {
    return `${e.author} submitted a pull request from ${e.from_branch || "unknown"} to ${e.to_branch || "unknown"} on ${time}`;
  }
  if (e.action === "MERGE") {
    return `${e.author} merged branch ${e.from_branch || "unknown"} to ${e.to_branch || "unknown"} on ${time}`;
  }
  return `${e.author} performed ${e.action} on ${time}`;
}

/**
 * Get CSS class for event action type
 * @param {string} action - The action type
 * @returns {string} CSS class name
 */
function getActionClass(action) {
  switch (action) {
    case "PUSH":
      return "event-push";
    case "PULL_REQUEST":
      return "event-pr";
    case "MERGE":
      return "event-merge";
    default:
      return "";
  }
}

/**
 * Create a list item element for an event
 * @param {Object} e - The event object
 * @returns {HTMLLIElement} The list item element
 */
function createEventElement(e) {
  const li = document.createElement("li");
  li.className = `event-item ${getActionClass(e.action)}`;
  li.innerHTML = `
    <span class="event-badge">${e.action}</span>
    <span class="event-text">${formatEvent(e)}</span>
  `;
  // Add fade-in animation for new events
  li.style.animation = "fadeIn 0.3s ease-in";
  return li;
}

/**
 * Fetch events from the server and update the UI.
 * Uses incremental fetching to only get new events.
 */
async function refresh() {
  try {
    // Build URL with optional 'since' parameter for incremental fetch
    let url = "/events?limit=50";
    if (lastSeenTimestamp) {
      url += `&since=${encodeURIComponent(lastSeenTimestamp)}`;
    }

    const res = await fetch(url);
    const data = await res.json();

    statusEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;

    if (data.length === 0 && !lastSeenTimestamp) {
      // No events at all yet
      feed.innerHTML = '<li class="no-events">No events yet. Waiting for webhooks...</li>';
      return;
    }

    // Remove the "no events" message if present
    const noEventsEl = feed.querySelector(".no-events");
    if (noEventsEl) {
      noEventsEl.remove();
    }

    // Process new events (they come sorted by timestamp descending)
    let newEventCount = 0;
    for (const e of data) {
      // Skip if we've already seen this event
      if (seenEventIds.has(e.request_id)) {
        continue;
      }

      // Mark as seen
      seenEventIds.add(e.request_id);
      newEventCount++;

      // Prepend new event to the feed
      const li = createEventElement(e);
      feed.insertBefore(li, feed.firstChild);

      // Update last seen timestamp (first event is the newest)
      if (!lastSeenTimestamp || e.timestamp > lastSeenTimestamp) {
        lastSeenTimestamp = e.timestamp;
      }
    }

    // Update event count
    countEl.textContent = seenEventIds.size;

  } catch (err) {
    statusEl.textContent = "Failed to load events. Retrying...";
    console.error("Error fetching events:", err);
  }
}

// Initial fetch
refresh();

// Poll every 15 seconds
setInterval(refresh, 15000);
