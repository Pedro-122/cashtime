from flask_cors import CORS
from flask import Flask, request, jsonify
from datetime import datetime
import requests

def enviar_para_utmify(payload):
    url = "https://api.utmify.com.br/api-credentials/orders"
    headers = {
        "Content-Type": "application/json",
        "x-api-token": "TOo1JcdVVXLWbp1DLdbgcfkHn99wgTsLycJy"
    }
    response = requests.post(url, json=payload, headers=headers)
    print('Utmify response:', response.status_code, response.text)
    return response.json()

app = Flask(__name__)

CORS(app)

# Dados do cliente fixo (sempre será gerado no nome dele)
CLIENTE_NOME = "Rede Solidária - Doação para Laura"
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
        "externalCode": "Rede Solidária - Doação para Laura",  # pode personalizar
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
                "title": "Vitoria",
                "description": "Russia",
                "unitPrice": valor_centavos,
                "quantity": 1,
                "tangible": False
            }
        ],
        "postbackUrl": "https://www.contribuavakinha.online/2",
        "ip": "127.0.0.1",
        "metadata": {
            "utm_source": data.get("utm_source"),
            "utm_medium": data.get("utm_medium"),
            "utm_campaign": data.get("utm_campaign"),
            "utm_content": data.get("utm_content"),
            "utm_term": data.get("utm_term"),
            "src": data.get("src"),
            "sck": data.get("sck"),
            "createdAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "approvedDate": data.get("approvedDate"),
            "orderId": data.get("orderId"),
        },
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

        # Montando payload da UTMIFY
        utmify_payload = {
            "orderId": response_json.get("orderId") or response_json.get("id"),
            "platform": "backend",
            "paymentMethod": "pix",
            "status": "waiting_payment",
            "createdAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "approvedDate": None,
            "refundedAt": None,
            "customer": {
                "name": CLIENTE_NOME,
                "email": CLIENTE_EMAIL,
                "phone": CLIENTE_TELEFONE,
                "document": CLIENTE_CPF,
                "country": "BR",
                "ip": request.remote_addr
            },
            "products": [
                {
                    "id": "1",
                    "name": "Vitoria",
                    "planId": None,
                    "planName": None,
                    "quantity": 1,
                    "priceInCents": int(float(valor) * 100)
                }
            ],
            "trackingParameters": {
                "src": data.get("src"),
                "sck": data.get("sck"),
                "utm_source": data.get("utm_source"),
                "utm_campaign": data.get("utm_campaign"),
                "utm_medium": data.get("utm_medium"),
                "utm_content": data.get("utm_content"),
                "utm_term": data.get("utm_term")
            },
            "commission": {
                "totalPriceInCents": int(float(valor) * 100),
                "gatewayFeeInCents": 0,
                "userCommissionInCents": int(float(valor) * 100)
            },
            "isTest": False
        }

        # Envia para UTMIFY
        enviar_para_utmify(utmify_payload)

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
