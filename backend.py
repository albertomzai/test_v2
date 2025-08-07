from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    """Serve the main page of the mortgage simulator.

    Returns:
        The rendered index.html file from the static folder.
    """
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # No external API is required for this project; therefore no .env or .gitignore are created.
    app.run(host='0.0.0.0', port=5000, debug=True)
