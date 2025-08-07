from flask import Flask, jsonify, request, send_from_directory
import os
import json
from pathlib import Path
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

TASKS_FILE = Path('tasks.json')

class Task:
    """Representa una tarea del tablero Kanban."""

    def __init__(self, id: int, content: str, status: str):
        self.id = id
        self.content = content
        self.status = status

    def to_dict(self) -> dict:
        """Convierte la tarea a un diccionario JSON serializable."""
        return {"id": self.id, "content": self.content, "status": self.status}


def load_tasks() -> list[Task]:
    """Carga las tareas desde TASKS_FILE.

    Returns:
        Lista de objetos Task. Si el archivo no existe devuelve una lista vacía.
    """
    if not TASKS_FILE.exists():
        return []
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [Task(**t) for t in data]
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_tasks(tasks: list[Task]) -> None:
    """Guarda la lista de tareas en TASKS_FILE."""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)

# Cargamos las tareas al iniciar el servidor
TASKS = load_tasks()
NEXT_ID = max((t.id for t in TASKS), default=0) + 1

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Endpoints REST
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Devuelve todas las tareas existentes."""
    return jsonify([t.to_dict() for t in TASKS])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Crea una nueva tarea.

    Expected JSON body:
        {"content": str, "status": str}
    """
    data = request.get_json(silent=True)
    if not data or 'content' not in data:
        return jsonify({"error": "Missing 'content' field."}), 400
    status = data.get('status', 'Por Hacer')
    new_task = Task(id=NEXT_ID, content=data['content'], status=status)
    global NEXT_ID
    NEXT_ID += 1
    TASKS.append(new_task)
    save_tasks(TASKS)
    return jsonify(new_task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Actualiza el contenido o estado de una tarea existente."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided."}), 400
    for task in TASKS:
        if task.id == task_id:
            task.content = data.get('content', task.content)
            task.status = data.get('status', task.status)
            save_tasks(TASKS)
            return jsonify(task.to_dict())
    return jsonify({"error": "Task not found."}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Elimina una tarea por su identificador."""
    global TASKS
    new_tasks = [t for t in TASKS if t.id != task_id]
    if len(new_tasks) == len(TASKS):
        return jsonify({"error": "Task not found."}), 404
    TASKS = new_tasks
    save_tasks(TASKS)
    return '', 204

if __name__ == '__main__':
    # No se crean archivos .env ni .gitignore porque no son necesarios
    app.run(host='0.0.0.0', port=5000, debug=True)