# tests/test_tasks.py
import json
from pathlib import Path
import tempfile
import pytest

# Import the functions from tasks module
from tasks import (
    cargar_tareas,
    guardar_tareas,
    generar_id_unico,
    obtener_tarea_por_id,
)

@pytest.fixture
def temp_tasks_file(tmp_path):
    """Create a temporary tasks.json file for each test."""
    file = tmp_path / 'tasks.json'
    # Monkey‑patch the module's TASKS_FILE path
    from tasks import TASKS_FILE as original
    import types
    tasks_module = types.ModuleType('tasks')
    tasks_module.TASKS_FILE = file
    yield file
    # Cleanup is handled by tmp_path

# Helper to load JSON directly for comparison

def load_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_generar_id_unico_empty(tmp_path):
    file = tmp_path / 'tasks.json'
    guardar_tareas([], file=file)
    assert generar_id_unico([]) == 1

def test_generar_id_unico_nonempty(tmp_path):
    tasks = [{'id': 2, 'contenido': 'x', 'estado': 'todo'}]
    file = tmp_path / 'tasks.json'
    guardar_tareas(tasks, file=file)
    assert generar_id_unico(tasks) == 3

def test_cargar_y_guardar(tmp_path):
    tasks = [
        {'id': 1, 'contenido': 'Test', 'estado': 'todo'},
        {'id': 2, 'contenido': 'Another', 'estado': 'doing'}
    ]
    file = tmp_path / 'tasks.json'
    guardar_tareas(tasks, file=file)
    loaded = cargar_tareas(file=file)
    assert loaded == tasks

def test_obtener_tarea_por_id(tmp_path):
    tasks = [
        {'id': 1, 'contenido': 'Task', 'estado': 'todo'},
        {'id': 2, 'contenido': 'Second', 'estado': 'doing'}
    ]
    file = tmp_path / 'tasks.json'
    guardar_tareas(tasks, file=file)
    assert obtener_tarea_por_id(tasks, 1)['contenido'] == 'Task'
    assert obtener_tarea_por_id(tasks, 3) is None
