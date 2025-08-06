from flask import Flask, jsonify, send_from_directory
import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()
API_KEY_EXTERNA = os.getenv("API_KEY_EXTERNA")
if not API_KEY_EXTERNA:
    raise RuntimeError("La variable de entorno API_KEY_EXTERNA no está definida.")

app = Flask(__name__, static_folder="static", static_url_path="")

@app.route('/')
def index():
    """Sirve el archivo index.html del directorio static."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/tiempo', methods=['GET'])
def obtener_clima():
    """Obtiene datos climáticos actuales de OpenWeatherMap.

    Returns:
        JSON con la temperatura y el estado del clima.
    """
    try:
        params = {
            'q': 'Madrid',  # Ciudad de ejemplo, puede modificarse
            'appid': API_KEY_EXTERNA,
            'units': 'metric',
            'lang': 'es'
        }
        response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        clima = {
            'ciudad': data.get('name'),
            'temperatura': data['main']['temp'],
            'descripcion': data['weather'][0]['description']
        }
        return jsonify(clima)
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'Error HTTP: {http_err}'}), 502
    except requests.exceptions.ConnectionError as conn_err:
        return jsonify({'error': f'Conexión fallida: {conn_err}'}), 502
    except Exception as err:
        return jsonify({'error': f'Ocurrió un error inesperado: {err}'}), 500

if __name__ == '__main__':
    # Crear archivo .env con la API_KEY_EXTERNA si no existe
    if not os.path.exists('.env'):
        with open('.env', 'w', encoding='utf-8') as f_env:
            f_env.write(f'API_KEY_EXTERNA={"08b86e71e806d896e60f7f73822a24cd"}\n')
    # Crear archivo .gitignore si no existe
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w', encoding='utf-8') as f_git:
            f_git.write('venv/\n.env\n__pycache__/\n')
    app.run(host='0.0.0.0', port=5000, debug=True)