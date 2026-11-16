# Roadmap & Architecture Plan - EDPay Python SDK

## Objectives
1. Develop a framework-agnostic Python client with synchronous and asynchronous support (via `httpx`).
2. Complete type annotations (Pydantic / TypedDicts / dataclasses) for excellent autocompletion in modern IDEs (PyCharm, VS Code, Cursor).
3. Ready-to-use native integrations for Django (`edpay.contrib.django`) and FastAPI (`edpay.contrib.fastapi`).

---

## Development Phases

### Phase 1: Core Client & Authentication (Completed)
- [x] Base client with `X-EDPay-Public-Key` and `X-EDPay-Private-Key` header injection.
- [x] Idempotency support via `Idempotency-Key`.
- [x] Automatic switching between `sandbox` (`https://sandbox-api.edpay.co.mz`) and `production` (`https://api.edpay.co.mz`).
- [x] HMAC SHA-256 signature verification for webhooks.

### Phase 2: Resource Modules (Completed)
- [x] `PaymentsResource`: `create`, `retrieve`, `cancel`.
- [x] `CheckoutResource`: `create_session`, `expire_session`.
- [x] `PaymentLinksResource`: `create`, `list`, `revoke`.
- [x] `CustomersResource`: `create`, `retrieve`, `update`.
- [x] `WebhooksResource`: `verify_signature`.

### Phase 3: Framework Integrations & Middleware (Planned)
- [ ] Django app with a webhook view and signal handlers (`edpay_payment_succeeded`).
- [ ] FastAPI dependency injection provider (`Depends(get_edpay_client)`).
- [ ] Pydantic v2 schemas for webhook deserialization.

### Phase 4: Testing & CI/CD
- [ ] Unit tests with `respx` mocking EDPay HTTP responses.
- [ ] GitHub Actions workflow for linting (`ruff`) and type checking (`mypy`).
- [ ] Publication on PyPI.
