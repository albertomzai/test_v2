# backend.py
"""
Flask application that serves the Kanban frontend and exposes a REST API
for task management.

The project structure is:
- app/
- static/index.html
- tasks.py (business logic)
- tests/test_tasks.py
"""

from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS
import os

# Initialize Flask application with static folder for the frontend.
app = Flask(__name__, static_folder='static')
CORS(app)  # Allow same‑origin requests from index.html

# ---------------------------------------------------------------------------
# Helper: load tasks module
# ---------------------------------------------------------------------------
from tasks import (
    cargar_tareas,
    guardar_tareas,
    generar_id_unico,
    obtener_tarea_por_id,
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    """Serve the single‑page application.

    The file is located in the ``static`` directory and named ``index.html``.
    """
    return send_from_directory(app.static_folder, 'index.html')

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks as JSON."""
    tareas = cargar_tareas()
    return jsonify(tareas), 200

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task.

    Expected JSON body:
        {
            "contenido": str,
            "estado": str
        }
    """
    if not request.is_json:
        abort(400, description='Request must be JSON')

    data = request.get_json()
    contenido = data.get('contenido', '').strip()
    estado = data.get('estado', '').strip()

    if not contenido or not estado:
        abort(400, description='Both "contenido" and "estado" are required')

    tareas = cargar_tareas()
    nuevo_id = generar_id_unico(tareas)
    nueva_tarea = {
        'id': nuevo_id,
        'contenido': contenido,
        'estado': estado
    }
    tareas.append(nueva_tarea)
    guardar_tareas(tareas)
    return jsonify(nueva_tarea), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task.

    JSON body may contain ``contenido`` and/or ``estado``.
    """
    if not request.is_json:
        abort(400, description='Request must be JSON')

    data = request.get_json()
    contenido = data.get('contenido')
    estado = data.get('estado')

    tareas = cargar_tareas()
    tarea = obtener_tarea_por_id(tareas, task_id)
    if not tarea:
        abort(404, description='Task not found')

    if contenido is not None:
        contenido = contenido.strip()
        if not contenido:
            abort(400, description='"contenido" cannot be empty')
        tarea['contenido'] = contenido
    if estado is not None:
        estado = estado.strip()
        if not estado:
            abort(400, description='"estado" cannot be empty')
        tarea['estado'] = estado

    guardar_tareas(tareas)
    return jsonify(tarea), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task by its ID."""
    tareas = cargar_tareas()
    tarea = obtener_tarea_por_id(tareas, task_id)
    if not tarea:
        abort(404, description='Task not found')

    tareas.remove(tarea)
    guardar_tareas(tareas)
    return jsonify({'message': 'Task deleted'}), 200

# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': error.description or 'Bad Request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': error.description or 'Not Found'}), 404

# ---------------------------------------------------------------------------
# Run the app (only when executed directly, not on import)
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Ensure tasks.json exists before starting.
    if not os.path.exists('tasks.json'):
        with open('tasks.json', 'w', encoding='utf-8') as f:
            f.write('[]')
    app.run(host='0.0.0.0', port=5000, debug=True)
