from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# In-memory storage for tasks during server session
TASKS: list[dict] = []

@app.route('/')
def index():
    """Serve the main page of the To-Do application.

    Returns:
        The index.html file from the static folder.
    """
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/tareas', methods=['POST'])
def handle_tareas():
    """Handle adding or removing tasks via a POST request.

    The request must contain JSON with the following structure:
        {
            "action": "add" | "remove",
            "task": {"id": int, "title": str}
        }

    Depending on the action, the task is appended to or removed from the in‑memory list.

    Returns:
        A JSON response with a status message and the current list of tasks.
    """
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    action = data.get('action')
    task = data.get('task')

    if action not in {'add', 'remove'} or not isinstance(task, dict):
        return jsonify({'error': 'Invalid payload'}), 400

    if action == 'add':
        # Avoid duplicate ids
        existing_ids = {t['id'] for t in TASKS}
        if task.get('id') in existing_ids:
            return jsonify({'error': 'Task ID already exists'}), 409
        TASKS.append(task)
    else:  # remove
        TASKS[:] = [t for t in TASKS if t.get('id') != task.get('id')]

    return jsonify({'status': f'Task {action}ed successfully', 'tasks': TASKS})

if __name__ == '__main__':
    # No external API, so no .env or gitignore creation needed.
    app.run(host='0.0.0.0', port=5000, debug=True)