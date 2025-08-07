#!/usr/bin/env python3
"""
Backend implementation for the Mini-Trello Kanban board.

This module sets up a Flask application that exposes CRUD endpoints for
managing tasks. Tasks are persisted in a JSON file (`tasks.json`).
The API follows the contract defined by the architect and includes
basic error handling and CORS support.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
TASKS_FILE = BASE_DIR / "tasks.json"
STATIC_FOLDER = BASE_DIR / "static"

# Ensure the static folder exists (used for serving index.html)
STATIC_FOLDER.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Flask application setup
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder=str(STATIC_FOLDER))
CORS(app)  # Allow CORS from any origin (frontend runs locally)

# ---------------------------------------------------------------------------
# In‑memory task store and helper functions
# ---------------------------------------------------------------------------
_tasks: List[Dict[str, object]] = []
_next_id: int = 1


def load_tasks() -> None:
    """Load tasks from the JSON file into memory.

    If the file does not exist or is empty, start with an empty list.
    The global ``_next_id`` is set to one more than the maximum existing id.
    """
    global _tasks, _next_id
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    _tasks = data
        except (json.JSONDecodeError, OSError) as exc:
            # Log the error; in a real app use logging module
            print(f"Failed to load tasks: {exc}")
    else:
        _tasks = []
    _next_id = max((task["id"] for task in _tasks), default=0) + 1


def persist_tasks() -> None:
    """Write the current list of tasks to ``tasks.json``.

    The operation is atomic by writing to a temporary file first and then
    replacing the original.
    """
    tmp_file = TASKS_FILE.with_suffix(".tmp")
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(_tasks, f, ensure_ascii=False, indent=2)
        tmp_file.replace(TASKS_FILE)
    except OSError as exc:
        print(f"Failed to persist tasks: {exc}")

# Load existing tasks on startup
load_tasks()

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Serve the frontend application.

    The index.html file should be placed inside the ``static`` folder.
    """
    return send_from_directory(app.static_folder, "index.html")

# API endpoints -------------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Return all tasks as a JSON array."""
    return jsonify({"tasks": _tasks})

@app.route("/api/tasks", methods=["POST"])
def create_task():
    """Create a new task.

    Expects JSON body with ``content`` and ``state`` keys. Returns the
    created task with its assigned ``id``.
    """
    if not request.is_json:
        abort(400, description="Request must be JSON")
    data = request.get_json()
    content = data.get("content")
    state = data.get("state")
    if not isinstance(content, str) or not isinstance(state, str):
        abort(400, description="'content' and 'state' must be strings")

    global _next_id
    task = {"id": _next_id, "content": content, "state": state}
    _tasks.append(task)
    _next_id += 1
    persist_tasks()
    return jsonify({"task": task}), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update an existing task.

    The JSON body may contain ``content`` and/or ``state``. Only the
    provided fields are updated.
    """
    if not request.is_json:
        abort(400, description="Request must be JSON")
    data = request.get_json()
    task = next((t for t in _tasks if t["id"] == task_id), None)
    if task is None:
        abort(404, description=f"Task with id {task_id} not found")

    content = data.get("content")
    state = data.get("state")
    if content is not None:
        if not isinstance(content, str):
            abort(400, description="'content' must be a string")
        task["content"] = content
    if state is not None:
        if not isinstance(state, str):
            abort(400, description="'state' must be a string")
        task["state"] = state

    persist_tasks()
    return jsonify({"task": task})

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete the specified task.

    Returns HTTP 204 No Content on success.
    """
    global _tasks
    initial_len = len(_tasks)
    _tasks = [t for t in _tasks if t["id"] != task_id]
    if len(_tasks) == initial_len:
        abort(404, description=f"Task with id {task_id} not found")
    persist_tasks()
    return '', 204

# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": error.description}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": error.description}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ---------------------------------------------------------------------------
# Test client entry point (optional for manual testing)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
