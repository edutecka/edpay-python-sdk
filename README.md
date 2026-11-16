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

## Continue the same payment with another method

The payment ID and reference identify one payment. Present active gateways as choices; each selected method is a child attempt, with only one attempt in progress at a time. Do not create another payment when the buyer changes method. Create the next attempt only after the current one is definitively failed. If it is still processing or its result is unknown, retrieve it later and wait for reconciliation to avoid charging twice. Use a new idempotency key for each child attempt.

```python
payment_id = payment["data"]["id"]  # save this ID with your order
current = client.payments.retrieve(payment_id)

if current["data"]["status"] == "failed":
    client.payments.create_attempt(
        payment_id,
        method=selected_method,  # active code from GET /v1/public/payment-methods
        phone=normalized_phone,
        idempotency_key="ORDER-10492-ATTEMPT-2",
    )
```

For a payment started through a hosted session or payment link, use the matching `create_session_payment_attempt` or `create_payment_link_payment_attempt` with that same payment ID and its session token/link ID. The current public checkout form accepts phone-based methods; use the partner payment resource for tokenized instruments.

## Function reference

Each row tells you what the call does and when to use it. Partner calls use the API key pair; public catalog and buyer checkout calls do not. Supply a stable `Idempotency-Key` for writes where required.

| Resource | Function | Endpoint | What it does / when to use it |
|---|---|---|---|
| Payments | `payments.create` | `POST /v1/payments` | Creates the parent payment and its first method attempt. Start a server-to-server payment; keep its ID and reference for later method attempts and status checks. |
| Payments | `payments.create_checkout` | `POST /v1/payment-checkout` | Legacy alias for creating a payment; it does not create a hosted checkout session. Use only when migrating an integration that already calls this route. New code should use create. |
| Payments | `payments.list` | `GET /v1/payments` | Lists payments visible to the current API credentials and environment. Reconcile or show a payment history. Use the limit argument where available. |
| Payments | `payments.retrieve` | `GET /v1/payments/{id}` | Returns one payment and its current status. Check the result on your server after a redirect or webhook. |
| Payments | `payments.events` | `GET /v1/payments/{id}/events` | Returns the recorded status changes for a payment. Inspect the payment lifecycle or troubleshoot a status change. |
| Payments | `payments.attempts` | `GET /v1/payments/{id}/attempts` | Lists the payment's provider attempts; this method is read-only. See which method was tried and the outcome of each attempt. |
| Payments | `payments.create_attempt` | `POST /v1/payments/{id}/attempts` | Adds another dynamic method as a child attempt. The payment ID, amount and reference stay the same; this attempt uses its own Idempotency-Key. Use after the latest attempt definitively failed. If it is processing or unknown, retrieve the payment and wait for reconciliation to avoid a duplicate charge. A payment supports up to 20 attempts. |
| Hosted checkout | `checkout.create_session` | `POST /v1/checkout/sessions` | Creates a short-lived checkout session from a payment link. Returns a token for the browser. Send a buyer to EDPay-hosted checkout or embed it on the exact HTTPS origin. |
| Hosted checkout | `checkout.retrieve_session` | `GET /v1/checkout/sessions/{token}` | Reads public session and checkout details. Pass the token returned by createSession. Load the hosted checkout page using its browser token. |
| Hosted checkout | `checkout.get_payment_link` | `GET /v1/checkout/payment-links/{id}` | Reads the public details for an active payment link. Render the buyer-facing link checkout before a payment is submitted. |
| Hosted checkout | `checkout.frame_policy` | `GET /v1/checkout/sessions/{token}/frame-policy` | Reads whether the session can be embedded and its frame policy. Check embed eligibility before placing checkout in an iframe. |
| Hosted checkout | `checkout.create_session_payment` | `POST /v1/checkout/sessions/{token}/payments` | Submits a selected phone-based method and buyer data to a public session; tokenized methods are not accepted by the current hosted form. Requires an idempotency key. Start payment from a hosted checkout form. The response means accepted for processing, not paid. |
| Hosted checkout | `checkout.create_session_payment_attempt` | `POST /v1/checkout/sessions/{token}/payments/{payment_id}/attempts` | Adds another phone-based method to the payment already created from this session. It keeps the same payment ID and reference; hosted checkout currently does not accept tokenized instruments. Use the same session token and payment ID after the previous attempt definitively failed. Wait when the result is processing or unknown. |
| Hosted checkout | `checkout.retrieve_session_payment` | `GET /v1/checkout/sessions/{token}/payments/{payment_id}` | Reads the status of a payment created from that session. Show a buyer the latest processing result; verify settlement server-side too. |
| Hosted checkout | `checkout.create_payment_link_payment` | `POST /v1/checkout/payment-links/{id}/payments` | Submits a selected phone-based method and buyer data from a public link; tokenized methods are not accepted by the current hosted form. Requires an idempotency key. Start a buyer payment directly from a payment-link page. |
| Hosted checkout | `checkout.create_payment_link_payment_attempt` | `POST /v1/checkout/payment-links/{id}/payments/{payment_id}/attempts` | Adds another phone-based method to the payment already created from this link. It keeps the same payment ID and reference; hosted checkout currently does not accept tokenized instruments. Reuse the same link ID and payment ID after the previous attempt definitively failed. Wait when the result is processing or unknown. |
| Hosted checkout | `checkout.retrieve_payment_link_payment` | `GET /v1/checkout/payment-links/{id}/payments/{payment_id}` | Reads the status of a payment submitted through a public link. Refresh the buyer-facing result for a link payment. |
| Payment links | `payment_links.create` | `POST /v1/payment-links` | Creates a fixed-amount public link. Creating the link does not itself create a payment. Collect payment for a fixed amount through a shareable buyer URL. |
| Payment links | `payment_links.list` | `GET /v1/payment-links` | Lists links owned by the authenticated account and environment. Show or reconcile the account's payment links. |
| Payment links | `payment_links.retrieve` | `GET /v1/payment-links/{id}` | Reads one link and its status. Check expiry, amount, or whether the link is still active. |
| Payment links | `payment_links.deactivate` | `POST /v1/payment-links/{id}/deactivate` | Stops an active link from starting future checkout payments. Close a link that should no longer accept buyer payments. |
| Payment links | `—` | `POST /v1/checkout/sessions` | Convenience wrapper that creates a hosted session for the supplied link. Use it instead of calling checkout.createSession when your SDK provides this wrapper. |
| Customers | `customers.create` | `POST /v1/customers` | Creates a customer record for the authenticated account. Save customer details before associating them with payments or invoices. |
| Customers | `customers.list` | `GET /v1/customers` | Lists customers in the current account and environment. Build a customer picker or reconcile customer records. |
| Customers | `customers.retrieve` | `GET /v1/customers/{id}` | Reads one customer record. Load a customer's saved details by ID. |
| Customers | `customers.update` | `PATCH /v1/customers/{id}` | Updates the supplied customer fields. Correct or refresh a customer's details; use a stable idempotency key where required. |
| Invoices | `invoices.create` | `POST /v1/invoices` | Creates a draft invoice with its customer and line items. Prepare an invoice before issuing it to the customer. |
| Invoices | `invoices.list` | `GET /v1/invoices` | Lists invoices, optionally limited to a page size. Show or reconcile invoices for the account. |
| Invoices | `invoices.get` | `GET /v1/invoices/{id}` | Reads one invoice and its current state. Load invoice details or check its lifecycle. |
| Invoices | `invoices.finalize` | `POST /v1/invoices/{id}/finalize` | Issues the draft invoice and makes it available for payment. The invoice is complete and ready to send to the customer. |
| Invoices | `invoices.void` | `POST /v1/invoices/{id}/void` | Voids an invoice that should no longer be payable. Cancel an issued invoice according to its allowed state transitions. |
| Invoice series | `subscriptions.create` | `POST /v1/invoice-series` | Creates a schedule that issues invoices on the configured interval. Bill a customer repeatedly using a defined start date, interval, and due period. |
| Invoice series | `subscriptions.list` | `GET /v1/invoice-series` | Lists invoice series; there is no series-detail endpoint in this API version. Review recurring schedules for the account. |
| Invoice series | `subscriptions.pause` | `POST /v1/invoice-series/{id}/pause` | Pauses future invoice generation for a series. Temporarily stop recurring billing without deleting the schedule. |
| Invoice series | `subscriptions.resume` | `POST /v1/invoice-series/{id}/resume` | Resumes invoice generation for a paused series. Restart recurring billing after the pause condition has ended. |
| FX quotes | `fx.quote` | `GET /v1/fx/quote` | Returns an indicative conversion quote for an amount and currency pair. Display a conversion estimate before creating a payment. A quote is not a settlement guarantee. |
| Wallets | `wallets.list` | `GET /v1/wallets` | Lists wallets available to the authenticated account and environment. Choose a wallet before reading its balance or entries. |
| Wallets | `wallets.retrieve` | `GET /v1/wallets/{id}` | Reads one wallet's details. Load the wallet metadata for an account view. |
| Wallets | `wallets.balance` | `GET /v1/wallets/{id}/balance` | Reads the wallet's current balance. Show the available or pending balance for a wallet. |
| Wallets | `wallets.entries` | `GET /v1/wallets/{id}/entries` | Lists ledger entries with cursor pagination. Show a transaction statement; pass the returned cursor for the next page. |
| Webhooks | `webhooks.list_endpoints` | `GET /v1/webhook-endpoints` | Lists configured webhook destinations. Review which event destinations are active. |
| Webhooks | `webhooks.create_endpoint` | `POST /v1/webhook-endpoints` | Registers an HTTPS receiver and selected event types. The signing secret is shown only at creation. Connect your server to receive payment lifecycle events; store the returned secret securely. |
| Webhooks | `webhooks.update_endpoint` | `PATCH /v1/webhook-endpoints/{id}` | Updates a destination's URL or subscribed event types. Change a receiver without creating a second endpoint. |
| Webhooks | `webhooks.disable_endpoint` | `POST /v1/webhook-endpoints/{id}/disable` | Stops future deliveries to an endpoint while retaining its record. Temporarily stop a destination while investigating or migrating it. |
| Webhooks | `webhooks.delete_endpoint` | `DELETE /v1/webhook-endpoints/{id}` | Removes a webhook endpoint. Permanently remove a destination that is no longer used. |
| Webhooks | `webhooks.list_deliveries` | `GET /v1/webhook-deliveries` | Lists delivery attempts and their summary states. Monitor failed, pending, or completed event deliveries. |
| Webhooks | `webhooks.retrieve_delivery` | `GET /v1/webhook-deliveries/{id}` | Reads one delivery's status and attempt metadata. Inspect one delivery before deciding whether to retry it. |
| Webhooks | `webhooks.retry_delivery` | `POST /v1/webhook-deliveries/{id}/retry` | Queues a retry for an eligible failed delivery. Retry after fixing the receiver; the endpoint must be active. |
| Public catalog and optional support chat | `public.list_payment_methods` | `GET /v1/public/payment-methods` | Returns active payment methods and their public requirements without partner keys. Build a method selector and validate the selected method's required fields. |
| Contact helpers | `normalize_phone_number` | `Local helper` | Removes display punctuation and returns the phone value in the configured national or international form. Prepare a phone value before validating or sending it to a method that requires one. |
| Contact helpers | `format_phone_number` | `Local helper` | Formats a valid phone number for display; it does not change the API payload automatically. Show a readable phone number in a form or confirmation screen. |
| Contact helpers | `add_country_prefix` | `Local helper` | Adds the configured country calling code to a national number. An integration needs the international form, such as 258 plus national digits. |
| Contact helpers | `remove_country_prefix` | `Local helper` | Removes the configured country calling code and returns national digits. A selected method expects the national number without a country code. |
| Contact helpers | `validate_phone_number` | `Local helper` | Checks length, allowed characters, country code, and configured prefixes; returns true or false. Reject invalid input before calling the API. It does not replace server-side validation. |
| Contact helpers | `phone_number_options_for_method` | `Local helper` | Returns known contact rules for the selected method, or None when no preset exists. Load rules before validating a phone; configure rules from the live catalog for other phone methods. |
| Webhook signature verification | `verify_webhook_signature` | `Local helper` | Checks the Payment-Signature HMAC and timestamp against the unmodified request body. Verify the signature before parsing or acting on an incoming webhook. Use the raw bytes and keep the secret server-side. |
| Client utilities | `client.request` | `Raw API request` | Sends a request to an API path without a dedicated resource wrapper. The authenticated argument controls whether partner key headers are sent. Use only for a supported endpoint that has no SDK method; keep private keys on the server and apply the endpoint's scope and idempotency rules. |

Responses are decoded Python dictionaries. API errors raise `EDPayException` with HTTP status and response data.
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
