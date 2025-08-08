#!/usr/bin/env python3
"""Entrypoint del servidor Flask.

Este archivo expone la ruta raíz que sirve el frontend (index.html) y configura
el blueprint de la aplicación.
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# Importar el blueprint de las rutas API
from app.routes import api_bp

app = Flask(__name__, static_folder="static")
CORS(app)  # Permite peticiones desde el mismo dominio sin cabeceras adicionales
app.register_blueprint(api_bp, url_prefix="/api")

@app.route("/")
def index():
    """Sirve la página principal del frontend."""
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    # Ejecutar en modo desarrollo con recarga automática
    app.run(host="0.0.0.0", port=5000, debug=True)
