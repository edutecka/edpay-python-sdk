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

Every partner API request requires both `EDPAY_PUBLIC_KEY` (`pk_test_` or `pk_live_`) and `EDPAY_PRIVATE_KEY` (`sk_test_` or `sk_live_`) from the same environment. The SDK rejects missing, blank, or mismatched key pairs when creating the client. Public catalog requests and buyer-facing checkout requests authenticated by a checkout token do not use the partner key pair; never put the private key in browser code. The matching key prefixes select test or live access; both use the single default host, https://api-pay.edutecka.com.

Create API keys in the EDPay merchant dashboard and keep the private key on your server. The SDK authenticates partner API requests using the `X-EDPay-Public-Key` and `X-EDPay-Private-Key` headers.

```bash
export EDPAY_PUBLIC_KEY=pk_test_...
export EDPAY_PRIVATE_KEY=sk_test_...
```

```python
import os
from edpay import EDPayClient, normalize_phone_number, phone_number_options_for_method

client = EDPayClient(
    public_key=os.environ["EDPAY_PUBLIC_KEY"],
    private_key=os.environ["EDPAY_PRIVATE_KEY"],
)

payment = client.payments.create(
    amount_minor=50000,  # 500.00 MZN
    currency="MZN",
    reference="ORDER-10492",
    description="Example order",
    idempotency_key="ORDER-10492-CREATE-1",
)
print(payment)
```

`amount_minor` is the amount in minor currency units. `payments.create` creates only the parent payment. Choose a dynamic method afterward through `private_checkout`, or let the buyer choose in hosted or link checkout. Method fields such as `phone` and `channel` belong to that child operation and depend on the selected method. Use an idempotency key when creating the parent. API errors are raised as `EDPayException` with the HTTP status and response data.

Populate a payment-method selector from the public catalog and use the active catalog codes as the buyer's available choices; the SDK does not hard-code gateway identifiers:

```python
catalog = client.public.list_payment_methods()
available_methods = [method for method in catalog["data"]["payment_methods"] if method["enabled"]]
```

## Choose a checkout mode for one payment

`payments.create` creates the parent record only. Save its ID and reference with your order, then choose the integration with a child function. The same payment can use private API processing, hosted checkout, or a shareable link checkout. The payment ID and reference stay unchanged.

```python
payment = client.payments.create(
    amount_minor=50000,
    currency="MZN",
    reference="ORDER-10492",
    idempotency_key="ORDER-10492-CREATE",
)
payment_id = payment["data"]["id"]

# Choose a mode for this parent payment:
checkout = client.payments.public_checkout(
    payment_id,
    idempotency_key="ORDER-10492-PUBLIC-CHECKOUT",
)
# Or call private_checkout(payment_id, method=..., ...) or link_checkout(payment_id, ...).
# Pass checkout["data"]["token"] to the buyer-facing page; never expose partner keys.
```

`private_checkout` submits a method from your backend. `public_checkout` returns an opaque token for hosted checkout. `link_checkout` returns a shareable token for this same payment. `list_checkouts(payment_id)` lists private executions, public/link executions, and sessions where no method was submitted; each execution keeps its originating checkout mode. `retrieve(payment_id)` fetches status from the API; use verified webhooks for asynchronous updates.

### M-Pesa and e-Mola PIN confirmation

For `method: "mpesa"` or `"emola"`, the provider's 60-second PIN window starts only after the Master delivers the charge. The API's 80-second `private-checkout` deadline starts with the API request, so validation, queueing, and dispatch latency already consume it; it does not wait another 80 seconds after the provider window starts. It returns HTTP `200` with a terminal attempt or `202` if the result is still pending, processing, or unknown when the deadline expires. The SDK transport timeout defaults to 90 seconds; keep a custom timeout above 80 seconds. If the caller disconnects, durable processing continues; configured webhook endpoints receive the event when the payment result is confirmed. You can also query `GET /v1/payments/{id}` and `GET /v1/payments/{id}/checkouts`. Do not resubmit while the attempt is pending or unknown.

## Function reference

Each row tells you what the call does and when to use it. Partner calls use the API key pair; public catalog and buyer checkout calls do not. Supply a stable `Idempotency-Key` for writes where required.

| Resource | Function | Endpoint | What it does / when to use it |
|---|---|---|---|
| Payments | `payments.create` | `POST /v1/payments` | Creates the parent payment only. Save its ID and reference, then choose a checkout mode. |
| Payments | `payments.private_checkout` | `POST /v1/payments/{id}/private-checkout` | Submits a selected method from your server for the existing payment. Use when your backend controls the interface. |
| Payments | `payments.public_checkout` | `POST /v1/payments/{id}/public-checkout` | Creates an opaque token for EDPay-hosted checkout on the existing payment. |
| Payments | `payments.link_checkout` | `POST /v1/payments/{id}/link-checkout` | Creates a shareable buyer token for the existing payment; it does not create another payment. |
| Payments | `payments.list_checkouts` | `GET /v1/payments/{id}/checkouts` | Lists executions with their checkout mode and sessions where no method was submitted. |
| Payments | `payments.retrieve` | `GET /v1/payments/{id}` | Retrieves remote payment status. |
| Payments | `payments.events` | `GET /v1/payments/{id}/events` | Reads recorded payment status changes. |
| Payments | `payments.list` | `GET /v1/payments` | Lists account payments for reconciliation or history. |
| Hosted checkout | `payments.get_checkout` | `GET /v1/payments/checkouts/{token}` | Loads the buyer-facing hosted or link checkout with its opaque token. |
| Hosted checkout | `payments.submit_checkout_payment` | `POST /v1/payments/checkouts/{token}/payment` | Submits the buyer-selected method and required method fields with an idempotency key. |
| Hosted checkout | `payments.retrieve_checkout_payment` | `GET /v1/payments/checkouts/{token}/payment` | Reads the parent payment status without exposing its ID to the buyer. |
| Hosted checkout | `payments.frame_policy` | `GET /v1/payments/checkouts/{token}/frame-policy` | Checks whether the hosted checkout can be embedded. |
| Customers | `customers.create` | `POST /v1/customers` | Creates a customer record for the authenticated account. Save customer details before associating them with payments or invoices. |
| Customers | `customers.list` | `GET /v1/customers` | Lists customers in the current account and environment. Build a customer picker or reconcile customer records. |
| Customers | `customers.retrieve` | `GET /v1/customers/{id}` | Reads one customer record. Load a customer's saved details by ID. |
| Customers | `customers.update` | `PATCH /v1/customers/{id}` | Updates the supplied customer fields. Correct or refresh a customer's details; use a stable idempotency key where required. |
| Invoices | `invoices.create` | `POST /v1/invoices` | Creates a draft invoice with its customer and line items. Prepare an invoice before issuing it to the customer. |
| Invoices | `invoices.list` | `GET /v1/invoices` | Lists invoices, optionally limited to a page size. Show or reconcile invoices for the account. |
| Invoices | `invoices.get` | `GET /v1/invoices/{id}` | Reads one invoice and its current state. Load invoice details or check its lifecycle. |
| Invoices | `invoices.finalize` | `POST /v1/invoices/{id}/finalize` | Issues the draft invoice and makes it available for payment. The invoice is complete and ready to send to the customer. |
| Invoices | `invoices.void` | `POST /v1/invoices/{id}/void` | Voids an invoice that should no longer be payable. Cancel an issued invoice according to its allowed state transitions. |
| Invoice series | `subscriptions.create` | `POST /v1/invoices/series` | Creates a schedule that issues invoices on the configured interval. Bill a customer repeatedly using a defined start date, interval, and due period. |
| Invoice series | `subscriptions.list` | `GET /v1/invoices/series` | Lists invoice series; there is no series-detail endpoint in this API version. Review recurring schedules for the account. |
| Invoice series | `subscriptions.pause` | `POST /v1/invoices/series/{id}/pause` | Pauses future invoice generation for a series. Temporarily stop recurring billing without deleting the schedule. |
| Invoice series | `subscriptions.resume` | `POST /v1/invoices/series/{id}/resume` | Resumes invoice generation for a paused series. Restart recurring billing after the pause condition has ended. |
| FX quotes | `fx.quote` | `GET /v1/fx/quote` | Returns an indicative conversion quote for an amount and currency pair. Display a conversion estimate before creating a payment. A quote is not a settlement guarantee. |
| Wallets | `wallets.list` | `GET /v1/wallets` | Lists wallets available to the authenticated account and environment. Choose a wallet before reading its balance or entries. |
| Wallets | `wallets.retrieve` | `GET /v1/wallets/{id}` | Reads one wallet's details. Load the wallet metadata for an account view. |
| Wallets | `wallets.balance` | `GET /v1/wallets/{id}/balance` | Reads the wallet's current balance. Show the available or pending balance for a wallet. |
| Wallets | `wallets.entries` | `GET /v1/wallets/{id}/entries` | Lists ledger entries with cursor pagination. Show a transaction statement; pass the returned cursor for the next page. |
| Webhooks | `webhooks.list_endpoints` | `GET /v1/webhooks/endpoints` | Lists configured webhook destinations. Review which event destinations are active. |
| Webhooks | `webhooks.create_endpoint` | `POST /v1/webhooks/endpoints` | Registers an HTTPS receiver and selected event types. The signing secret is shown only at creation. Connect your server to receive payment lifecycle events; store the returned secret securely. |
| Webhooks | `webhooks.update_endpoint` | `PATCH /v1/webhooks/endpoints/{id}` | Updates a destination's URL or subscribed event types. Change a receiver without creating a second endpoint. |
| Webhooks | `webhooks.disable_endpoint` | `POST /v1/webhooks/endpoints/{id}/disable` | Stops future deliveries to an endpoint while retaining its record. Temporarily stop a destination while investigating or migrating it. |
| Webhooks | `webhooks.delete_endpoint` | `DELETE /v1/webhooks/endpoints/{id}` | Removes a webhook endpoint. Permanently remove a destination that is no longer used. |
| Webhooks | `webhooks.list_deliveries` | `GET /v1/webhooks/deliveries` | Lists delivery attempts and their summary states. Monitor failed, pending, or completed event deliveries. |
| Webhooks | `webhooks.retrieve_delivery` | `GET /v1/webhooks/deliveries/{id}` | Reads one delivery's status and attempt metadata. Inspect one delivery before deciding whether to retry it. |
| Webhooks | `webhooks.retry_delivery` | `POST /v1/webhooks/deliveries/{id}/retry` | Queues a retry for an eligible failed delivery. Retry after fixing the receiver; the endpoint must be active. |
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
