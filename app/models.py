"""Modelo de datos para las tareas Kanban."""

from dataclasses import dataclass, field
from typing import List
import json
import os

TASKS_FILE = "tasks.json"
DEFAULT_STATE = "Por Hacer"

@dataclass
class Task:
    """Representa una tarea con id, contenido y estado."""
    id: int
    content: str
    state: str = field(default=DEFAULT_STATE)

    def to_dict(self) -> dict:
        """Convierte la instancia a un diccionario serializable en JSON."""
        return {"id": self.id, "content": self.content, "state": self.state}

    @staticmethod
    def from_dict(data: dict):
        """Crea una Task desde un diccionario.

        Args:
            data: Un diccionario con las claves 'id', 'content' y opcionalmente 'state'.

        Returns:
            Task: Instancia creada a partir de los datos.
        """
        return Task(
            id=data["id"],
            content=data["content"],
            state=data.get("state", DEFAULT_STATE),
        )

# Funciones de acceso al almacenamiento JSON ---------------------------------

def _load_tasks() -> List[Task]:
    """Carga la lista completa de tareas desde el archivo JSON.

    Si el archivo no existe, devuelve una lista vacía.
    """
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Task.from_dict(item) for item in data]
    except (json.JSONDecodeError, OSError):  # Manejo de errores comunes
        return []

def _save_tasks(tasks: List[Task]) -> None:
    """Guarda la lista de tareas en el archivo JSON.

    Args:
        tasks: Lista de instancias Task a persistir.
    """
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump([task.to_dict() for task in tasks], f, indent=2)

# Operaciones CRUD ------------------------------------------------------------

def get_all_tasks() -> List[Task]:
    return _load_tasks()

def add_task(content: str) -> Task:
    tasks = _load_tasks()
    new_id = max((t.id for t in tasks), default=0) + 1
    task = Task(id=new_id, content=content)
    tasks.append(task)
    _save_tasks(tasks)
    return task

def update_task(task_id: int, *, content: str | None = None, state: str | None = None) -> Task:
    tasks = _load_tasks()
    for t in tasks:
        if t.id == task_id:
            if content is not None:
                t.content = content
            if state is not None:
                t.state = state
            _save_tasks(tasks)
            return t
    raise KeyError(f"Task with id {task_id} not found")

def delete_task(task_id: int) -> None:
    tasks = _load_tasks()
    new_tasks = [t for t in tasks if t.id != task_id]
    if len(new_tasks) == len(tasks):  # No se encontró el id
        raise KeyError(f"Task with id {task_id} not found")
    _save_tasks(new_tasks)
