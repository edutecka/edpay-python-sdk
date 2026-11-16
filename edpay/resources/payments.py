from typing import Any, Dict, Optional
from urllib.parse import quote


class PaymentsResource:
    def __init__(self, client):
        self._client = client

    def create(
        self,
        amount_minor: int,
        currency: str,
        method: Optional[str] = None,
        phone: Optional[str] = None,
        customer_id: Optional[str] = None,
        reference: Optional[str] = None,
        description: Optional[str] = None,
        channel: Optional[Dict[str, Any]] = None,
        *,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """Create a direct payment intent. Phone and channel fields depend on method."""
        payload: Dict[str, Any] = {
            "amount_minor": amount_minor,
            "currency": currency,
        }
        if method is not None:
            payload["method"] = method
        if phone is not None:
            payload["phone"] = phone
        if customer_id:
            payload["customer_id"] = customer_id
        if reference:
            payload["reference"] = reference
        if description:
            payload["description"] = description
        if channel is not None:
            payload["channel"] = channel
        return self._client.request("POST", "/v1/payments", json_data=payload, idempotency_key=idempotency_key)

    def create_checkout(self, payload: Dict[str, Any], idempotency_key: str) -> Dict[str, Any]:
        """Legacy alias for creating a payment intent through /v1/payment-checkout."""
        return self._client.request("POST", "/v1/payment-checkout", json_data=payload, idempotency_key=idempotency_key)

    def list(self, limit: int = 50) -> Dict[str, Any]:
        return self._client.request("GET", "/v1/payments", params={"limit": limit})

    def retrieve(self, payment_id: str) -> Dict[str, Any]:
        """Retrieve a payment's status by its unique identifier."""
        return self._client.request("GET", f"/v1/payments/{quote(payment_id, safe='')}")

    def events(self, payment_id: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/payments/{quote(payment_id, safe='')}/events")

    def attempts(self, payment_id: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/payments/{quote(payment_id, safe='')}/attempts")
