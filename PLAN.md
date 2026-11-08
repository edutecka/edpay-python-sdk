# Roadmap & Plano de Arquitetura - EDPay Python SDK

## Objectivos
1. Desenvolver um cliente Python agnóstico de framework com suporte síncrono e assíncrono (via `httpx`).
2. Type annotations completas (Pydantic / TypedDicts / dataclasses) para autocompletion perfeito em IDEs modernos (PyCharm, VS Code, Cursor).
3. Integrações nativas prontas para Django (`edpay.contrib.django`) e FastAPI (`edpay.contrib.fastapi`).

---

## Fases de Desenvolvimento

### Fase 1: Core Client & Autenticação (Concluído)
- [x] Cliente base com injeção dos headers `X-EDPay-Public-Key` e `X-EDPay-Private-Key`.
- [x] Suporte a idempotência via `Idempotency-Key`.
- [x] Alternância automática entre `sandbox` (`https://sandbox-api.edpay.co.mz`) e `production` (`https://api.edpay.co.mz`).
- [x] Validação de assinatura HMAC SHA-256 para webhooks.

### Fase 2: Módulos de Recursos (Concluído)
- [x] `PaymentsResource`: `create`, `retrieve`, `cancel`.
- [x] `CheckoutResource`: `create_session`, `expire_session`.
- [x] `PaymentLinksResource`: `create`, `list`, `revoke`.
- [x] `CustomersResource`: `create`, `retrieve`, `update`.
- [x] `WebhooksResource`: `verify_signature`.

### Fase 3: Framework Integrations & Middlewares (Em Planeamento)
- [ ] Django App com webhook view e signal handlers (`edpay_payment_succeeded`).
- [ ] FastAPI Dependency injection provider (`Depends(get_edpay_client)`).
- [ ] Pydantic v2 schemas para deserialização de webhooks.

### Fase 4: Testes & CI/CD
- [ ] Testes unitários com `respx` mockando respostas HTTP da EDPay.
- [ ] GitHub Actions workflow para lint (`ruff`) e tipagem (`mypy`).
- [ ] Publicação no PyPI.
