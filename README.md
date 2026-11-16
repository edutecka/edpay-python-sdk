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
from edpay import EDPayClient, normalize_phone_number, phone_number_options_for_method

client = EDPayClient(
    public_key=os.environ["EDPAY_PUBLIC_KEY"],
    private_key=os.environ["EDPAY_PRIVATE_KEY"],
    environment="sandbox",
    base_url="https://api-pay.edutecka.com",
)

method = os.environ["EDPAY_METHOD"]
phone_rules = phone_number_options_for_method(method)
phone = (
    normalize_phone_number(os.environ.get("CUSTOMER_PHONE", ""), **phone_rules)
    if phone_rules is not None
    else None
)

payment = client.payments.create(
    amount_minor=50000,  # 500.00 MZN
    currency="MZN",
    method=method,
    phone=phone,
    reference="ORDER-10492",
    description="Example order",
    idempotency_key="ORDER-10492-CREATE-1",
)
print(payment)
```

`amount_minor` is the amount in minor currency units. `method` can be omitted only when the API's default method applies; otherwise select a dynamic ID from the public catalog. `phone` is optional for methods that do not need one. Tokenized methods pass their instrument through `channel`. Use test keys for sandbox requests and an idempotency key when retrying a create request. API errors are raised as `EDPayException` with the HTTP status and response data.

Populate a payment-method selector from the public catalog and pass the user's selected `code` to `payments.create`; the SDK does not hard-code gateway identifiers:

```python
catalog = client.public.list_payment_methods()
available_methods = [method for method in catalog["data"]["payment_methods"] if method["enabled"]]
```

## Create a hosted checkout session

```python
session = client.checkout.create_session(
    payment_link_id=os.environ["EDPAY_PAYMENT_LINK_ID"],
    idempotency_key="ORDER-10492-CHECKOUT-1",
)
print(session)
```

The response includes a short-lived `data.token`, not a checkout URL. Pass the token and public key to your browser checkout code. Confirm the final payment state from a verified webhook or by retrieving the payment; do not rely only on a browser redirect.

## Verify an EDPay webhook in FastAPI

Install FastAPI and an ASGI server separately for this example:

```bash
python -m pip install fastapi uvicorn
export EDPAY_WEBHOOK_SECRET=your_webhook_secret
```

```python
import os
from typing import cast
from fastapi import FastAPI, HTTPException, Request
from edpay import EDPayWebhookEvent
from edpay.webhooks import verify_webhook_signature

app = FastAPI()

@app.post("/webhooks/edpay")
async def edpay_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("payment-signature", "")
    if not verify_webhook_signature(
        raw_body, signature, os.environ["EDPAY_WEBHOOK_SECRET"]
    ):
        raise HTTPException(status_code=400, detail="Invalid signature")

    event = cast(EDPayWebhookEvent, await request.json())
    if event.get("type") == "payment.succeeded":
        payment_link_id = event.get("data", {}).get("payment_link_id")
        # Update the matching order idempotently using event data.
        pass
    return {"received": True}
```

Save this handler as `app.py` and run it with `uvicorn app:app`. The SDK verifies the timestamped `Payment-Signature` over the unmodified raw request body and rejects timestamps outside its default five-minute window.

`EDPayWebhookEvent` and `EDPayWebhookPaymentData` describe the verified event envelope and sanitized payment fields. `data.payment_link_id` is nullable; reconciliation status/code and fee/net breakdown fields are optional because they are not present in every event. The verifier returns a boolean, so parse/cast only after signature verification.

## Format and validate a contact

The contact helpers default to Mozambique's calling code and nine national digits. They accept configurable country and selected-method prefix rules:

```python
import os
from edpay import add_country_prefix, format_phone_number, normalize_phone_number, phone_number_options_for_method, remove_country_prefix, validate_phone_number

phone = os.environ.get("CUSTOMER_PHONE", "")
rules = phone_number_options_for_method(os.environ.get("EDPAY_METHOD", ""))
if rules is not None:  # None means this method has no known phone preset.
    if not validate_phone_number(phone, **rules):
        raise ValueError("Phone number is invalid for the selected method")
    request_value = normalize_phone_number(phone, **rules)
    display = format_phone_number(phone, **rules)
    international = add_country_prefix(phone, **rules)
    national = remove_country_prefix(phone, **rules)
```

`phone_number_options_for_method(method)` supplies the known rules for `emola` (national `86`/`87`, output `national`) and `mpesa` (`84`/`85`, output `country-code`, i.e. `258` plus national digits). It returns `None` for other method identifiers, including non-phone methods; use account-provided rules for other phone methods and skip phone validation for tokenized methods. Rules remain configurable.

The support-chat route streams server-sent events and is not exposed by this release's JSON request helpers.

## Available operations

- Payments: `create`, `create_checkout`, `list`, `retrieve`, `events`, `attempts`
- Checkout: session creation/retrieval, frame policy, and checkout payment creation/retrieval
- Payment links: `create`, `list`, `retrieve`, `deactivate`, hosted session creation
- Customers: `create`, `list`, `retrieve`, `update`
- Invoices: `create`, `list`, `get`, `finalize`, `void`; invoice series: `create`, `list`, `pause`, `resume`
- FX quotes, wallets and ledger entries, public payment-method catalog, webhook endpoints and delivery retry
- Contact formatting, prefix management, and validation helpers
- Webhook signature verification: `verify_webhook_signature`

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
