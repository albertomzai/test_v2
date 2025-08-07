#!/usr/bin/env python3
"""
Unit tests for the Mini‑Trello backend.
They use Flask's test client to exercise each endpoint.
"""
import json
from pathlib import Path

import pytest
from backend import app, _load_tasks, _save_tasks, TASKS_FILE

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_storage(tmp_path):
    """Reset the tasks.json file before each test.
    The fixture writes an empty list to the file used by the app.
    """
    tmp_file = Path(tmp_path) / "tasks.json"
    # Monkey‑patch the module constant for isolation
    app.config["TASKS_FILE"] = str(tmp_file)
    global TASKS_FILE
    TASKS_FILE = str(tmp_file)
    _save_tasks([])
    yield
    # Clean up is handled by pytest tmp_path fixture

@pytest.fixture
def client():
    return app.test_client()

# ---------------------------------------------------------------------------
# Helper to create a task via the API
# ---------------------------------------------------------------------------
def create_task(client, content="Test", status=None):
    payload = {"content": content}
    if status:
        payload["status"] = status
    return client.post("/api/tasks", json=payload)

# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------
def test_get_empty(client):
    resp = client.get("/api/tasks")
    assert resp.status_code == 200
    assert resp.json == []

def test_create_task_default_status(client):
    resp = create_task(client, "Hello world")
    assert resp.status_code == 201
    data = resp.json
    assert data["content"] == "Hello world"
    assert data["status"] == "Por Hacer"
    # Verify persistence
    tasks = _load_tasks()
    assert len(tasks) == 1
    assert tasks[0]["id"] == data["id"]

def test_create_task_with_status(client):
    resp = create_task(client, "In progress", status="En Progreso")
    assert resp.status_code == 201
    assert resp.json["status"] == "En Progreso"

def test_update_task_content_and_status(client):
    post_resp = create_task(client, "Old content")
    task_id = post_resp.json["id"]
    put_resp = client.put(f"/api/tasks/{task_id}", json={"content": "New", "status": "Hecho"})
    assert put_resp.status_code == 200
    data = put_resp.json
    assert data["content"] == "New"
    assert data["status"] == "Hecho"

def test_delete_task(client):
    post_resp = create_task(client, "To be deleted")
    task_id = post_resp.json["id"]
    del_resp = client.delete(f"/api/tasks/{task_id}")
    assert del_resp.status_code == 200
    assert del_resp.json["message"] == f"Task {task_id} deleted"
    # Ensure it's gone
    get_resp = client.get("/api/tasks")
    assert task_id not in [t["id"] for t in get_resp.json]

def test_404_on_nonexistent_task(client):
    resp = client.put("/api/tasks/999", json={"content": "Doesn't matter"})
    assert resp.status_code == 404

# ---------------------------------------------------------------------------
# Run tests if executed directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    pytest.main([__file__])
