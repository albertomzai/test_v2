from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    """Serve the main page of the application.

    Returns:
        The ``index.html`` file located in the static folder.
    """
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # No external API, therefore no .env or .gitignore creation is required.
    app.run(host='0.0.0.0', port=5000, debug=True)