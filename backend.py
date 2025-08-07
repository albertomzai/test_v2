from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)  # Permite peticiones desde el dominio del frontend

@app.route('/')
def index():
    """Sirve la página principal index.html del directorio static."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/hipoteca', methods=['POST'])
def calcular_hipoteca():
    """Calcula una tabla de amortización para un préstamo.

    Expected JSON payload:
        {"monto": float, "tasa": float (en %), "plazo": int (meses)}

    Returns:
        200 OK con JSON: lista de objetos por cada cuota mensual.
        Cada objeto contiene:
            - mes: int
            - pago_total: float
            - interes: float
            - principal: float
            - saldo_restante: float
    """
    try:
        datos = request.get_json()
        monto = float(datos.get('monto'))
        tasa_annual = float(datos.get('tasa')) / 100.0
        plazo_meses = int(datos.get('plazo'))
    except (TypeError, ValueError) as e:
        return jsonify({'error': 'Formato de datos inválido', 'details': str(e)}), 400

    # Calcular la cuota mensual usando la fórmula estándar
    if tasa_annual == 0:
        pago_mensual = monto / plazo_meses
    else:
        tasa_mensual = tasa_annual / 12.0
        pago_mensual = monto * (tasa_mensual * (1 + tasa_mensual) ** plazo_meses) / ((1 + tasa_mensual) ** plazo_meses - 1)

    tabla = []
    saldo_restante = monto
    for mes in range(1, plazo_meses + 1):
        interes = saldo_restante * (tasa_annual / 12.0)
        principal = pago_mensual - interes
        saldo_restante -= principal
        if saldo_restante < 0:
            saldo_restante = 0.0
        tabla.append({
            'mes': mes,
            'pago_total': round(pago_mensual, 2),
            'interes': round(interes, 2),
            'principal': round(principal, 2),
            'saldo_restante': round(saldo_restante, 2)
        })

    return jsonify(tabla), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)