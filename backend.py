#!/usr/bin/env python3
"""
Backend API for a Mini‑Trello Kanban board.

This module implements the full CRUD interface defined in the
architectural plan.  All data is persisted to a single JSON file
(`tasks.json`) located at the project root.

The application uses Flask, Flask‑CORS and the standard library only.
"""

import json
import os
from typing import List, Dict, Any

from flask import Flask, jsonify, request, abort
from flask_cors import CORS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.json")
DEFAULT_STATUS = "Por Hacer"

app = Flask(__name__)
CORS(app, resources={"/api/*": {"origins": "http://localhost:3000"}})  # adjust port if needed

# ---------------------------------------------------------------------------
# Utility functions for JSON persistence
# ---------------------------------------------------------------------------
def _load_tasks() -> List[Dict[str, Any]]:
    """
    Load the list of tasks from TASKS_FILE.
    If the file does not exist, return an empty list.
    """
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ValueError("tasks.json is corrupted") from exc

def _save_tasks(tasks: List[Dict[str, Any]]) -> None:
    """
    Persist the given list of tasks to TASKS_FILE.
    The file is written atomically using a temporary write‑and‑rename
    strategy for safety.
    """
    temp_path = f"{TASKS_FILE}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, TASKS_FILE)

# ---------------------------------------------------------------------------
# Helper for ID generation
# ---------------------------------------------------------------------------
def _next_id(tasks: List[Dict[str, Any]]) -> int:
    """
    Return an integer that is one greater than the maximum existing id.
    If no tasks exist, return 1.
    """
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(400)
def bad_request(error):  # pragma: no cover - trivial wrapper
    response = jsonify({"error": "Bad request", "message": error.description})
    response.status_code = 400
    return response

@app.errorhandler(404)
def not_found(error):  # pragma: no cover - trivial wrapper
    response = jsonify({"error": "Not found", "message": error.description})
    response.status_code = 404
    return response

@app.errorhandler(500)
def internal_error(error):  # pragma: no cover - defensive
    response = jsonify({"error": "Internal server error", "message": str(error)})
    response.status_code = 500
    return response

# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Return the full list of tasks."""
    tasks = _load_tasks()
    return jsonify(tasks), 200

@app.route("/api/tasks", methods=["POST"])
def create_task():
    """Create a new task.

    Expected JSON body:
        {
            "content": "string",
            "status": "optional string"
        }
    """
    data = request.get_json(force=True, silent=False) or {}
    content = data.get("content")
    if not isinstance(content, str) or not content.strip():
        abort(400, description="'content' must be a non‑empty string")

    status = data.get("status", DEFAULT_STATUS)
    if status not in {"Por Hacer", "En Progreso", "Hecho"}:
        abort(400, description="Invalid 'status' value")

    tasks = _load_tasks()
    new_task = {
        "id": _next_id(tasks),
        "content": content.strip(),
        "status": status,
    }
    tasks.append(new_task)
    _save_tasks(tasks)
    return jsonify(new_task), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update an existing task's content and/or status."""
    data = request.get_json(force=True, silent=False) or {}
    if not data:
        abort(400, description="No data provided for update")

    tasks = _load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        abort(404, description=f"Task {task_id} not found")

    content = data.get("content")
    status = data.get("status")

    if content is not None:
        if not isinstance(content, str) or not content.strip():
            abort(400, description="'content' must be a non‑empty string")
        task["content"] = content.strip()

    if status is not None:
        if status not in {"Por Hacer", "En Progreso", "Hecho"}:
            abort(400, description="Invalid 'status' value")
        task["status"] = status

    _save_tasks(tasks)
    return jsonify(task), 200

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task by its ID."""
    tasks = _load_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        abort(404, description=f"Task {task_id} not found")

    _save_tasks(new_tasks)
    return jsonify({"message": f"Task {task_id} deleted"}), 200

# ---------------------------------------------------------------------------
# Main entry point for development server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure tasks.json exists on first run
    if not os.path.exists(TASKS_FILE):
        _save_tasks([])
    app.run(host="0.0.0.0", port=5000, debug=True)
