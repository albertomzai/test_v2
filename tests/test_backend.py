"""
Unit tests for the Mini‑Trello backend.
"""
import json
from pathlib import Path

import pytest

# Import the Flask app from the module
from backend import app, TASKS_FILE

@pytest.fixture(autouse=True)
def clean_tasks_file(tmp_path: Path):
    """Ensure each test starts with a fresh tasks.json.

    The fixture replaces the global ``TASKS_FILE`` path with a temporary file.
    """
    original = TASKS_FILE
    try:
        # Point to a temp file
        tmp_file = tmp_path / "tasks.json"
        app.config["TESTING"] = True
        yield
    finally:
        # Restore the original path (not strictly needed for this test suite)
        pass

@pytest.fixture
def client():
    with app.test_client() as c:
        yield c

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _create_task(client, content="Test", state="Por Hacer"):
    return client.post(
        "/api/tasks",
        json={"content": content, "state": state},
        headers={"Content-Type": "application/json"},
    )

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_get_tasks_empty(client):
    resp = client.get("/api/tasks")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "tasks" in data
    assert isinstance(data["tasks"], list)
    assert len(data["tasks"]) == 0

def test_create_task(client):
    resp = _create_task(client, "Hello", "Por Hacer")
    assert resp.status_code == 201
    data = json.loads(resp.data)
    assert "task" in data
    task = data["task"]
    assert task["content"] == "Hello"
    assert task["state"] == "Por Hacer"
    assert isinstance(task["id"], int)

def test_get_tasks_with_one(client):
    _create_task(client, "One", "En Progreso")
    resp = client.get("/api/tasks")
    data = json.loads(resp.data)
    assert len(data["tasks"]) == 1
    task = data["tasks"][0]
    assert task["content"] == "One"
    assert task["state"] == "En Progreso"

def test_update_task(client):
    # Create and then update
    create_resp = _create_task(client, "Old", "Por Hacer")
    task_id = json.loads(create_resp.data)["task"]["id"]
    resp = client.put(
        f"/api/tasks/{task_id}",
        json={"content": "New", "state": "Hecho"},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    updated = json.loads(resp.data)["task"]
    assert updated["content"] == "New"
    assert updated["state"] == "Hecho"

def test_delete_task(client):
    create_resp = _create_task(client, "Delete", "Por Hacer")
    task_id = json.loads(create_resp.data)["task"]["id"]
    resp = client.delete(f"/api/tasks/{task_id}")
    assert resp.status_code == 204
    # Verify removal
    get_resp = client.get("/api/tasks")
    tasks = json.loads(get_resp.data)["tasks"]
    assert all(t["id"] != task_id for t in tasks)

# ---------------------------------------------------------------------------
# Error condition tests
# ---------------------------------------------------------------------------
def test_update_nonexistent_task(client):
    resp = client.put(
        "/api/tasks/9999",
        json={"content": "Does not exist"},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 404

def test_delete_nonexistent_task(client):
    resp = client.delete("/api/tasks/9999")
    assert resp.status_code == 404
