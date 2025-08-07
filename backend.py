from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def index():
    """Serve the main page of the application."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/hipoteca', methods=['POST'])
def calcular_hipoteca():
    """Calculate mortgage amortization schedule.

    Expected JSON payload:
        {
            "importe": float,
            "tasa_interes": float,  # annual interest rate in percent
            "plazo": int           # number of months
        }

    Returns a JSON object with the amortization table:
        {"cuotas": [
            {"mes": int, "pago": float, "interes": float,
             "principal": float, "saldo": float}
         ]}

    Raises a 400 error if input validation fails.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    try:
        importe = float(data.get('importe'))
        tasa_interes = float(data.get('tasa_interes'))
        plazo = int(data.get('plazo'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Missing or invalid parameters'}), 400

    if importe <= 0 or tasa_interes < 0 or plazo <= 0:
        return jsonify({'error': 'Parameters must be positive numbers'}), 400

    # Monthly interest rate as decimal
    r = tasa_interes / 100.0 / 12.0
    # Monthly payment using annuity formula
    if r == 0:
        pago_mensual = importe / plazo
    else:
        pago_mensual = importe * (r * (1 + r) ** plazo) / ((1 + r) ** plazo - 1)

    tabla = []
    saldo_actual = importe
    for mes in range(1, plazo + 1):
        interes_mes = saldo_actual * r
        principal_mes = pago_mensual - interes_mes
        saldo_actual -= principal_mes
        if saldo_actual < 0:
            saldo_actual = 0.0
        tabla.append({
            'mes': mes,
            'pago': round(pago_mensual, 2),
            'interes': round(interes_mes, 2),
            'principal': round(principal_mes, 2),
            'saldo': round(saldo_actual, 2)
        })

    return jsonify({'cuotas': tabla})

if __name__ == '__main__':
    # No external API key needed; just start the server.
    app.run(host='0.0.0.0', port=5000, debug=True)