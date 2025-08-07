from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def index():
    """Serves the main page from the static folder."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/hipoteca', methods=['POST'])
def calcular_hipoteca():
    """Calculates an amortization schedule for a mortgage.

    Expects JSON payload with:
        - monto (float): loan amount in the local currency.
        - tasa_interes (float): annual interest rate expressed as a percentage.
        - plazo (int): term of the loan in years.

    Returns a JSON object containing:
        - tabla (list[dict]): each entry has mes, pago, interes, principal, saldo.
        - total_pago (float): sum of all monthly payments.
        - total_interes (float): sum of all interest payments.
    """
    try:
        data = request.get_json(force=True)
        monto = float(data.get('monto'))
        tasa_interes = float(data.get('tasa_interes')) / 100.0
        plazo = int(data.get('plazo'))
    except (TypeError, ValueError) as e:
        return jsonify({'error': 'Invalid input data', 'details': str(e)}), 400

    meses = plazo * 12
    tasa_mensual = tasa_interes / 12.0
    # Monthly payment using the amortization formula
    if tasa_mensual == 0:
        pago_mensual = monto / meses
    else:
        pago_mensual = monto * (tasa_mensual * (1 + tasa_mensual) ** meses) / ((1 + tasa_mensual) ** meses - 1)

    saldo = monto
    tabla = []
    total_interes = 0.0
    for mes in range(1, meses + 1):
        interes = saldo * tasa_mensual
        principal = pago_mensual - interes
        saldo -= principal
        if saldo < 0:
            saldo = 0.0
        tabla.append({
            'mes': mes,
            'pago': round(pago_mensual, 2),
            'interes': round(interes, 2),
            'principal': round(principal, 2),
            'saldo': round(saldo, 2)
        })
        total_interes += interes
    total_pago = pago_mensual * meses

    return jsonify({
        'tabla': tabla,
        'total_pago': round(total_pago, 2),
        'total_interes': round(total_interes, 2)
    })

if __name__ == '__main__':
    # Create requirements.txt if it does not exist
    if not os.path.exists('requirements.txt'):
        with open('requirements.txt', 'w') as f:
            f.write('Flask\nFlask-Cors\npython-dotenv\n')
    # Create .gitignore for common Python artifacts
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write('# Byte-compiled / optimized / DLL files\n__pycache__/\n*.py[cod]\n# Virtual environment\nvenv/\n# Environment variables\n.env\n')
    app.run(host='0.0.0.0', port=5000, debug=True)