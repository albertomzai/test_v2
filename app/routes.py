"""Rutas API RESTful para gestionar tareas Kanban."""

from flask import Blueprint, request, jsonify, abort
from typing import Any

from .models import (
    get_all_tasks,
    add_task,
    update_task,
    delete_task,
)

api_bp = Blueprint("api", __name__)

# ---------------------------------------------------------------------------
# Helpers de validación
# ---------------------------------------------------------------------------

def _validate_json(required_keys: list[str]) -> dict:
    if not request.is_json:
        abort(400, description="Request must be JSON")
    data = request.get_json(silent=True)
    if data is None:
        abort(400, description="Malformed JSON payload")
    missing = [k for k in required_keys if k not in data]
    if missing:
        abort(400, description=f"Missing keys: {', '.join(missing)}")
    return data

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@api_bp.route("/tasks", methods=["GET"])
def get_tasks():
    """Devuelve todas las tareas en formato JSON."""
    tasks = [t.to_dict() for t in get_all_tasks()]
    return jsonify(tasks), 200

@api_bp.route("/tasks", methods=["POST"])
def create_task():
    """Crea una nueva tarea.

    Espera un JSON con la clave 'content'. El estado se inicializa a 'Por Hacer' y se genera un id único.
    """
    data = _validate_json(["content"])
    content = str(data["content"]).strip()
    if not content:
        abort(400, description="Content cannot be empty")
    task = add_task(content)
    return jsonify(task.to_dict()), 201

@api_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def modify_task(task_id):
    """Actualiza el contenido o estado de una tarea existente."""
    data = request.get_json(silent=True) or {}
    content = data.get("content")
    state = data.get("state")
    if content is not None:
        content = str(content).strip()
        if not content:
            abort(400, description="Content cannot be empty")
    try:
        task = update_task(task_id, content=content, state=state)
    except KeyError as exc:
        abort(404, description=str(exc))
    return jsonify(task.to_dict()), 200

@api_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    """Elimina una tarea por su id."""
    try:
        delete_task(task_id)
    except KeyError as exc:
        abort(404, description=str(exc))
    return jsonify({"message": f"Task {task_id} deleted successfully"}), 200
