"""Pruebas unitarias básicas para la API de tareas."""

import json
from pathlib import Path

import pytest
from backend import app as flask_app

# Configurar el cliente de pruebas Flask
@pytest.fixture(scope="module")
def client():
    with flask_app.test_client() as client:
        yield client

# Helper para limpiar el archivo JSON antes de cada prueba
@pytest.fixture(autouse=True)
def reset_tasks_file(tmp_path):
    # Reemplazar la ruta del archivo por un temporal
    from app import models
    original = models.TASKS_FILE
    temp = tmp_path / "tasks.json"
    models.TASKS_FILE = str(temp)
    yield
    models.TASKS_FILE = original

def test_create_task(client):
    response = client.post("/api/tasks", json={"content": "Test task"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["content"] == "Test task"
    assert data["state"] == "Por Hacer"

def test_get_tasks(client):
    client.post("/api/tasks", json={"content": "First"})
    client.post("/api/tasks", json={"content": "Second"})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    tasks = response.get_json()
    assert len(tasks) == 2

def test_update_task(client):
    # Crear tarea
    res = client.post("/api/tasks", json={"content": "To update"})
    task_id = res.get_json()["id"]
    # Actualizar estado
    upd_res = client.put(f"/api/tasks/{task_id}", json={"state": "En Progreso"})
    assert upd_res.status_code == 200
    updated = upd_res.get_json()
    assert updated["state"] == "En Progreso"

def test_delete_task(client):
    res = client.post("/api/tasks", json={"content": "Delete me"})
    task_id = res.get_json()["id"]
    del_res = client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 200
    msg = del_res.get_json()
    assert f"{task_id} deleted successfully" in msg["message"]
