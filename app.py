from flask_cors import CORS
from flask import Flask, request, jsonify
from datetime import datetime
import requests

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
        # Dados de tracking/campanha
        "utm_source": data.get("utm_source"),
        "utm_medium": data.get("utm_medium"),
        "utm_campaign": data.get("utm_campaign"),
        "utm_content": data.get("utm_content"),
        "utm_term": data.get("utm_term"),
        "src": data.get("src"),
        "sck": data.get("sck"),

        # Identificadores e conciliação
        "orderId": data.get("orderId"),  # Se tiver, senão será o id do próprio gateway
        "transactionId": data.get("transactionId"),  # Caso gere um id próprio
        "customer_email": data.get("customer_email") or CLIENTE_EMAIL,
        "customer_phone": data.get("customer_phone") or CLIENTE_TELEFONE,
        "customer_name": data.get("customer_name") or CLIENTE_NOME,
        "customer_document": data.get("customer_document") or CLIENTE_CPF,

        # Informações de datas e status
        "createdAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "approvedDate": data.get("approvedDate"),   # Geralmente preenchido só após pagamento
        "refundedAt": data.get("refundedAt"),       # Preencha apenas se relevante

        "status": data.get("status") or "waiting_payment",  # ou status da Cashtime

        # Plataforma e meio de pagamento
        "platform": data.get("platform") or "web",    # ou "mobile", se distinguir
        "paymentMethod": data.get("paymentMethod") or "pix",

        # Outras informações úteis para debug
        "userAgent": data.get("userAgent"),
        "ip": data.get("ip") or request.remote_addr,

        # Identifica se é um teste (para não poluir analytics)
        "isTest": data.get("isTest") or False,

        # Produto/operação (se aplicável)
        "product_id": data.get("product_id"),
        "product_title": data.get("product_title"),
        "product_desc": data.get("product_desc"),
        "product_amount": data.get("product_amount") or valor_centavos,
    }
    # ... (restante do payload)
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
