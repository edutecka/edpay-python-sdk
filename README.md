# EDPay Python SDK

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

SDK oficial da EDPay para integração server-to-server com Python (FastAPI, Django, Flask ou scripts autónomos).

A plataforma EDPay é uma infraestrutura multi-gateway agnóstica em Moçambique, processando pagamentos via carteiras móveis (M-Pesa, e-Mola), cartões Visa/Mastercard com 3DS, Apple Pay, Google Pay e referências bancárias.

---

## Instalação

```bash
pip install edpay
```

Ou com `poetry` / `pipenv`:
```bash
poetry add edpay
```

---

## Inicialização

```python
from edpay import EDPayClient

client = EDPayClient(
    public_key="pk_live_...",
    private_key="sk_live_...",
    environment="production",  # ou "sandbox"
)
```

---

## Criar um Pagamento

```python
payment = client.payments.create(
    amount_minor=50000,           # 500.00 MZN
    currency="MZN",
    method="emola",               # ou "mpesa", "card", "apple_pay", etc.
    phone="+25884xxxxxxx",        # obrigatório para mobile wallets
    reference="FAT-2026-001",
    description="Assinatura Mensal",
    emola_custom_message="Pagamento de Servicos via EDPay",
    customer={
        "name": "Carlos Tembe",
        "email": "carlos@exemplo.co.mz",
    },
)

print(payment["id"])
print(payment["status"])  # "processing", "succeeded", "failed"
```

---

## Verificar Assinatura de Webhook

A EDPay assina todos os eventos de webhook com HMAC SHA-256 no header `X-EDPay-Signature`.

```python
from edpay.webhooks import verify_webhook_signature

# No FastAPI
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/webhook/edpay")
async def edpay_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("x-edpay-signature", "")
    secret = "whsec_..."

    if not verify_webhook_signature(payload, signature, secret):
        raise HTTPException(status_code=400, detail="Invalid signature")

    event = await request.json()
    if event["event"] == "payment.succeeded":
        payment_id = event["data"]["id"]
        # Atualizar encomenda na base de dados
        print(f"Pagamento aprovado: {payment_id}")

    return {"received": True}
```

---

## Prazos e Condições Comerciais

- **Tarifa Unificada**: 6,00% em Meticais (MZN) sem custos ocultos de adesão.
- **Liquidação Bancária**: Transferência direta para a conta do comerciante entre 2 a 7 dias úteis.

---

## Suporte & Comunidade

- Documentação da API: [https://docs.edpay.co.mz](https://docs.edpay.co.mz)
- Dashboard e Sandbox: [https://edpay.co.mz/dashboard](https://edpay.co.mz/dashboard)
- Contacto de Engenharia: `dev@edutecka.com`
