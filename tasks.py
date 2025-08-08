# tasks.py
"""
Business logic for managing Kanban tasks.

All operations are performed on a JSON file named ``tasks.json`` in the
project root. The module exposes functions to load, save, generate unique
IDs and retrieve tasks by ID.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

TASKS_FILE = Path(__file__).parent.parent / 'tasks.json'

# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------
def cargar_tareas() -> List[Dict]:
    """Load tasks from ``tasks.json``.

    Returns an empty list if the file does not exist or is invalid.
    """
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, ValueError):
        # Corrupted file – start fresh
        return []

def guardar_tareas(tareas: List[Dict]) -> None:
    """Persist the given task list to ``tasks.json``.

    The file is written atomically by writing to a temporary file and then
    replacing the original.
    """
    tmp_file = TASKS_FILE.with_suffix('.tmp')
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(tareas, f, ensure_ascii=False, indent=2)
    tmp_file.replace(TASKS_FILE)

# ---------------------------------------------------------------------------
# ID generation and lookup
# ---------------------------------------------------------------------------
def generar_id_unico(tareas: List[Dict]) -> int:
    """Return a new unique integer ID.

    The ID is one greater than the maximum existing ID, or 1 if no tasks.
    """
    if not tareas:
        return 1
    max_id = max(t['id'] for t in tareas)
    return max_id + 1

def obtener_tarea_por_id(tareas: List[Dict], task_id: int) -> Optional[Dict]:
    """Return the task with ``task_id`` or ``None`` if not found."""
    return next((t for t in tareas if t['id'] == task_id), None)
