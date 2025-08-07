"""
Flask backend for a mini‑Trello Kanban board.

The application exposes CRUD operations on a local JSON file
(`tasks.json`).  The data model is represented by the ``Task``
class.  CORS support is enabled so that the single‑page front‑end can
communicate with this API.

All paths and error handling follow the style guidelines from the
project’s `guia_de_estilo`.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_testing import TestCase

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)  # allow same‑origin requests – simple for dev environment

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class Task:
    id: int
    contenido: str
    estado: str

    def to_dict(self) -> dict:
        """Return a serialisable representation of the task."""
        return asdict(self)

# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------
def _load_tasks() -> List[Task]:
    """Load tasks from ``tasks.json``.

    If the file does not exist, an empty list is returned.  Any I/O errors
    are re‑raised to surface during development.
    """
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Task(**item) for item in data]

def _save_tasks(tasks: List[Task]) -> None:
    """Persist the provided list of tasks to ``tasks.json``.

    The file is written with UTF‑8 encoding and an indentation level of 2
    for human readability.
    """
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)

# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Return all stored tasks as JSON."""
    tasks = _load_tasks()
    return jsonify([t.to_dict() for t in tasks])

@app.route("/api/tasks", methods=["POST"])
def create_task():
    """Create a new task.

    Expected JSON payload:
        {"contenido": "<text>", "estado": "Por Hacer"}
    """
    data = request.get_json(silent=True) or {}
    contenido = data.get("contenido")
    estado = data.get("estado", "Por Hacer")

    if not isinstance(contenido, str) or not contenido.strip():
        return jsonify({"error": "'contenido' is required and must be a non‑empty string."}), 400

    tasks = _load_tasks()
    new_id = max((t.id for t in tasks), default=0) + 1
    task = Task(id=new_id, contenido=contenido.strip(), estado=estado)
    tasks.append(task)
    _save_tasks(tasks)
    return jsonify(task.to_dict()), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update the content or state of an existing task.

    Payload may contain either or both fields:
        {"contenido": "<text>", "estado": "En Progreso"}
    """
    data = request.get_json(silent=True) or {}
    contenido = data.get("contenido")
    estado = data.get("estado")

    if contenido is not None and (not isinstance(contenido, str) or not contenido.strip()):
        return jsonify({"error": "'contenido' must be a non‑empty string."}), 400

    tasks = _load_tasks()
    task = next((t for t in tasks if t.id == task_id), None)
    if task is None:
        return jsonify({"error": f"Task with id {task_id} not found."}), 404

    if contenido is not None:
        task.contenido = contenido.strip()
    if estado is not None:
        task.estado = estado

    _save_tasks(tasks)
    return jsonify(task.to_dict())

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task by its ID."""
    tasks = _load_tasks()
    new_tasks = [t for t in tasks if t.id != task_id]
    if len(new_tasks) == len(tasks):
        return jsonify({"error": f"Task with id {task_id} not found."}), 404
    _save_tasks(new_tasks)
    return jsonify({"mensaje": f"Task {task_id} deleted successfully."})

# ---------------------------------------------------------------------------
# Static file serving (index.html is the SPA entry point)
# ---------------------------------------------------------------------------
@app.route("/")
def serve_index():
    """Serve the single‑page application located in ``static/index.html``."""
    return send_from_directory(STATIC_DIR, "index.html")

# ---------------------------------------------------------------------------
# Testing suite using Flask‑Testing
# ---------------------------------------------------------------------------
class BaseTestCase(TestCase):
    def create_app(self):
        app.testing = True
        return app

    def setUp(self):
        # Ensure a clean state before each test
        if os.path.exists(TASKS_FILE):
            os.remove(TASKS_FILE)

class TaskApiTestCase(BaseTestCase):
    def test_create_and_get_task(self):
        payload = {"contenido": "Test task", "estado": "Por Hacer"}
        resp = self.client.post("/api/tasks", json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.json
        self.assertIn("id", data)
        self.assertEqual(data["contenido"], payload["contenido"])

        get_resp = self.client.get("/api/tasks")
        self.assertEqual(get_resp.status_code, 200)
        tasks = get_resp.json
        self.assertIsInstance(tasks, list)
        self.assertGreater(len(tasks), 0)

    def test_update_task(self):
        # Create first
        payload = {"contenido": "Old", "estado": "Por Hacer"}
        resp = self.client.post("/api/tasks", json=payload)
        task_id = resp.json["id"]

        update_payload = {"contenido": "New", "estado": "En Progreso"}
        upd_resp = self.client.put(f"/api/tasks/{task_id}", json=update_payload)
        self.assertEqual(upd_resp.status_code, 200)
        updated = upd_resp.json
        self.assertEqual(updated["contenido"], "New")
        self.assertEqual(updated["estado"], "En Progreso")

    def test_delete_task(self):
        payload = {"contenido": "To be deleted", "estado": "Por Hacer"}
        resp = self.client.post("/api/tasks", json=payload)
        task_id = resp.json["id"]

        del_resp = self.client.delete(f"/api/tasks/{task_id}")
        self.assertEqual(del_resp.status_code, 200)
        msg = del_resp.json
        self.assertIn("deleted successfully", msg.get("mensaje", ""))

        # Verify it no longer exists
        get_resp = self.client.get(f"/api/tasks/{task_id}")
        self.assertEqual(get_resp.status_code, 404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
