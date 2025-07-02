const express = require('express');
const axios = require('axios');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// --- CREDENCIAIS SANDBOX (ajuste com os seus dados reais) ---
const SECRET_KEY = 'sk_live_W6WN+8711RpClzcmGLBwxN+T5b6h6qBfwfuwCF5jVvw92hCtiOD7lBGMZChMTgnfNGGO/nrN/FsISixACN8SbGk2u6VIE/aUTkOlFTPo8HtuLvWd3WbH1IeukfhPNkqa2fDyOJM6DoH0V3FisfHIkmMlyNPs09iSV3CimOiMM4k=';
const PUBLIC_KEY = 'pk_live_jKZtkHMY5m7VZPWcLYTPKB0UF0AN6xEYA0P4KDsjWF/XFypD5A9gdQYCCQvB+gOZqfe9tIIvB+Li30c4MegeXg==';

// --- Função para obter token de autenticação da Cashtime ---
async function obterToken() {
    const resposta = await axios.post('https://staging.api.cashtime.com.br/v1/oauth/token', {
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        grant_type: 'client_credentials'
    });
    return resposta.data.access_token;
}

// --- Rota teste ---
app.get('/', (req, res) => {
    res.send('Backend Cashtime está funcionando!');
});

// --- Rota para gerar cobrança Pix ---
app.post('/criar-pagamento', async (req, res) => {
    try {
        const token = await obterToken();

        const pagamento = {
            amount: req.body.amount || 1700, // valor em centavos
            description: 'Doação via site',
            callback_url: 'https://seusite.com.br/status' // coloque depois seu link
        };

        const resposta = await axios.post(
            'https://staging.api.cashtime.com.br/v1/transactions',
            pagamento,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        res.json(resposta.data);
    } catch (erro) {
        console.error('Erro ao criar pagamento:', erro.response?.data || erro.message);
        res.status(500).json({ erro: 'Erro ao criar pagamento' });
    }
});

// --- Inicia o servidor ---
app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
});

// --- Rota para criar cobrança PIX ---
app.post('/criar-pix', async (req, res) => {
  try {
    const { nome, cpf, telefone, valor } = req.body;

    const token = await obterToken();

    const resposta = await axios.post('https://staging.api.cashtime.com.br/v1/pix/charge', {
      payer: {
        name: nome,
        document: cpf,
        phone: telefone
      },
      amount: valor,
      description: 'Pagamento via PIX',
      type: 'DYNAMIC'
    }, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    // Retorna o código PIX e o QR Code para a página 4
    res.json({
      copiaECola: resposta.data.code,
      qrCode: resposta.data.qrCodeImageUrl
    });

  } catch (erro) {
    console.error('Erro ao criar cobrança PIX:', erro.response?.data || erro.message);
    res.status(500).json({ erro: 'Falha ao criar cobrança PIX' });
  }
});

