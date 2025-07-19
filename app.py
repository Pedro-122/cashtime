from flask_cors import CORS
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CORS(app)

# Dados do cliente fixo (sempre será gerado no nome dele)
CLIENTE_NOME = "Rede Solidária - Laura"
CLIENTE_CPF = "40.881.302/0001-30"
CLIENTE_TELEFONE = "4896486390"  # sem espaço
CLIENTE_EMAIL = "antoniojoseramos123@gmail.com"

PUBLIC_KEY = "pk_live_jKZtkHMY5m7VZPWcLYTPKB0UF0AN6xEYA0P4KDsjWF/XFypD5A9gdQYCCQvB+gOZqfe9tIIvB+Li30c4MegeXg=="
SECRET_KEY = "sk_live_W6WN+8711RpClzcmGLBwxN+T5b6h6qBfwfuwCF5jVvw92hCtiOD7lBGMZChMTgnfNGGO/nrN/FsISixACN8SbGk2u6VIE/aUTkOlFTPo8HtuLvWd3WbH1IeukfhPNkqa2fDyOJM6DoH0V3FisfHIkmMlyNPs09iSV3CimOiMM4k="

CASHTIME_URL = "https://api.cashtime.com.br/v1/transactions"

@app.route('/criar-pix', methods=['POST'])
def criar_pix():
    data = request.json
    valor = data.get('valor')  # Valor em reais, ex: 17.00

    if not valor:
        return jsonify({'erro': 'Valor não informado'}), 400

    valor_centavos = int(float(valor) * 100)

    payload = {
        "isInfoProducts": True,
        "externalCode": "pix-antonio-ramos",  # pode personalizar
        "discount": 0,
        "paymentMethod": "pix",
        "installments": 1,
        "installmentsTax": 0,
        "customer": {
            "name": CLIENTE_NOME,
            "email": CLIENTE_EMAIL,
            "phone": CLIENTE_TELEFONE,
            "document": {
                "number": CLIENTE_CPF,
                "type": "cpf"
            }
        },
        
        "items": [
            {
                "title": "Doação",
                "description": "Doação voluntária",
                "unitPrice": valor_centavos,
                "quantity": 1,
                "tangible": False
            }
        ],
        "postbackUrl": "https://seudominio.com.br/postback",
        "ip": "127.0.0.1",
        "metadata": {},
        "subvendor": {},
        "amount": valor_centavos
    }

    headers = {
        "Content-Type": "application/json",
        "x-store-key": PUBLIC_KEY,
        "x-authorization-key": SECRET_KEY
    }

    try:
        response = requests.post(CASHTIME_URL, headers=headers, json=payload)
        response_json = response.json()

        qr_code = response_json.get('pix', {}).get('encodedImage')
        codigo_pix = response_json.get('pix', {}).get('payload')

        return jsonify({
            "qr_code": qr_code,
            "codigo_pix": codigo_pix,
            "cashtime_response": response_json
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
