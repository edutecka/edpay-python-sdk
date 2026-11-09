# EDPay Python SDK

Python client for sending server-to-server requests to the EDPay API.

## Requirements

- Python 3.9 or later
- pip

## Install

Install the SDK:

```bash
python -m pip install "git+https://github.com/edutecka/edpay-python-sdk.git"
```

## Create a payment

Create API keys in the EDPay merchant dashboard and keep the private key on your server. The SDK authenticates partner API requests using the `X-EDPay-Public-Key` and `X-EDPay-Private-Key` headers.

```bash
export EDPAY_PUBLIC_KEY=pk_test_...
export EDPAY_PRIVATE_KEY=sk_test_...
export EDPAY_METHOD=method_id_from_payment_methods
```

Choose `EDPAY_METHOD` from the IDs returned by `GET /v1/public/payment-methods`. The method identifier is dynamic; the required fields depend on the selected method.

```python
import os
from edpay import EDPayClient

client = EDPayClient(
    public_key=os.environ["EDPAY_PUBLIC_KEY"],
    private_key=os.environ["EDPAY_PRIVATE_KEY"],
    environment="sandbox",
    base_url="https://api-pay.edutecka.com",
)

payment = client.payments.create(
    amount_minor=50000,  # 500.00 MZN
    currency="MZN",
    method=os.environ["EDPAY_METHOD"],
    phone="+25884xxxxxxx",  # Optional; use only when required by the selected method.
    reference="ORDER-10492",
    description="Example order",
    idempotency_key="ORDER-10492",
)
print(payment)
```

`amount_minor` is the amount in minor currency units. Use test keys for sandbox requests and an idempotency key when retrying a create request. API errors are raised as `EDPayException` with the HTTP status and response data.

## Create a hosted checkout session

```python
session = client.checkout.create_session(
    amount_minor=50000,
    currency="MZN",
    success_url="https://merchant.example/checkout/success",
    cancel_url="https://merchant.example/checkout/cancel",
    reference="ORDER-10492",
    idempotency_key="ORDER-10492-checkout",
)
print(session)
```

Redirect the customer to the hosted checkout URL in the API response. Confirm the final payment state from a verified webhook or by retrieving the payment; do not rely only on the browser return URL.

## Verify an EDPay webhook in FastAPI

Install FastAPI and an ASGI server separately for this example:

```bash
python -m pip install fastapi uvicorn
export EDPAY_WEBHOOK_SECRET=your_webhook_secret
```

```python
import os
from fastapi import FastAPI, HTTPException, Request
from edpay.webhooks import verify_webhook_signature

app = FastAPI()

@app.post("/webhooks/edpay")
async def edpay_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("x-edpay-signature", "")
    if not verify_webhook_signature(
        raw_body, signature, os.environ["EDPAY_WEBHOOK_SECRET"]
    ):
        raise HTTPException(status_code=400, detail="Invalid signature")

    event = await request.json()
    if event.get("type") == "payment.succeeded":
        # Update the matching order idempotently using event data.
        pass
    return {"received": True}
```

Save the example as `app.py` and run it with `uvicorn app:app`. Verify the signature against the unmodified raw request body before processing an event.

## Available operations

- Payments: `create`, `retrieve`, `cancel`
- Checkout sessions: `create_session`, `retrieve_session`, `expire_session`
- Payment links: `create`, `retrieve`, `revoke`
- Customers: `create`, `retrieve`, `update`
- Invoices: `create`, `get`, `list`, `finalize`, `void`
- Subscriptions: `create`, `get`, `list`, `pause`, `resume`
- Webhooks: `verify_webhook_signature`

The client returns decoded JSON responses as Python dictionaries. Use the resource methods above to retrieve IDs and payment status from the API response.

## Documentation

- [EDPay SDK integration guide](https://docs-pay.edutecka.com/sdks/)
- [Payments API reference](https://docs-pay.edutecka.com/api/payments/)
- [Authentication and API keys](https://docs-pay.edutecka.com/guides/authentication/)
- [Webhooks](https://docs-pay.edutecka.com/api/webhooks/)

## License

MIT. See [LICENSE](LICENSE).

## Official SDK repositories

- [JavaScript / TypeScript](https://github.com/edutecka/edpay-javascript-sdk)
- [PHP](https://github.com/edutecka/edpay-php-sdk)
- [Java](https://github.com/edutecka/edpay-java-sdk)
- [.NET](https://github.com/edutecka/edpay-dot-net-sdk)
- [Python](https://github.com/edutecka/edpay-python-sdk)

## Official e-commerce plugin repositories

These repositories contain integration previews; check each project README for its implementation status and limitations before use.

- [WooCommerce (WordPress)](https://github.com/edutecka/edpay-woocommerce-plugin)
- [Shopify](https://github.com/edutecka/edpay-shopify-app)
- [Magento / Adobe Commerce](https://github.com/edutecka/edpay-magento2-module)
- [PrestaShop](https://github.com/edutecka/edpay-prestashop-module)
- [OpenCart](https://github.com/edutecka/edpay-opencart-extension)
- [WHMCS](https://github.com/edutecka/edpay-whmcs-gateway)
