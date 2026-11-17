from typing import Any, Dict, Optional
from urllib.parse import quote


class PaymentsResource:
    def __init__(self, client):
        self._client = client

    def create(self, amount_minor: int, currency: str, customer_id: Optional[str] = None,
               reference: Optional[str] = None, description: Optional[str] = None,
               *, idempotency_key: str) -> Dict[str, Any]:
        """Create the payment parent. Choose a checkout mode afterwards."""
        payload: Dict[str, Any] = {"amount_minor": amount_minor, "currency": currency}
        if customer_id is not None: payload["customer_id"] = customer_id
        if reference is not None: payload["reference"] = reference
        if description is not None: payload["description"] = description
        return self._client.request("POST", "/v1/payments", json_data=payload, idempotency_key=idempotency_key)

    def private_checkout(self, payment_id: str, method: str, phone: Optional[str] = None,
                         channel: Optional[Dict[str, Any]] = None, *, idempotency_key: str) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"method": method}
        if phone is not None: payload["phone"] = phone
        if channel is not None: payload["channel"] = channel
        return self._client.request("POST", f"/v1/payments/{quote(payment_id, safe='')}/private-checkout", json_data=payload, idempotency_key=idempotency_key)

    def public_checkout(self, payment_id: str, embed_origin: Optional[str] = None,
                        *, idempotency_key: str) -> Dict[str, Any]:
        payload = {"embed_origin": embed_origin} if embed_origin else {}
        return self._client.request("POST", f"/v1/payments/{quote(payment_id, safe='')}/public-checkout", json_data=payload, idempotency_key=idempotency_key)

    def link_checkout(self, payment_id: str, expires_at: Optional[str] = None,
                      *, idempotency_key: str) -> Dict[str, Any]:
        payload = {"expires_at": expires_at} if expires_at else {}
        return self._client.request("POST", f"/v1/payments/{quote(payment_id, safe='')}/link-checkout", json_data=payload, idempotency_key=idempotency_key)

    def list_checkouts(self, payment_id: str) -> Dict[str, Any]:
        """List checkout executions with their mode and sessions with no submission."""
        return self._client.request("GET", f"/v1/payments/{quote(payment_id, safe='')}/checkouts")

    def get_checkout(self, token: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/payments/checkouts/{quote(token, safe='')}", authenticated=False)

    def submit_checkout_payment(self, token: str, method: str, phone: Optional[str] = None,
                                channel: Optional[Dict[str, Any]] = None, *, idempotency_key: str) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"method": method}
        if phone is not None: payload["phone"] = phone
        if channel is not None: payload["channel"] = channel
        return self._client.request("POST", f"/v1/payments/checkouts/{quote(token, safe='')}/payment", json_data=payload, idempotency_key=idempotency_key, authenticated=False)

    def retrieve_checkout_payment(self, token: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/payments/checkouts/{quote(token, safe='')}/payment", authenticated=False)

    def frame_policy(self, token: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/payments/checkouts/{quote(token, safe='')}/frame-policy", authenticated=False)

    def list(self, limit: int = 50) -> Dict[str, Any]:
        return self._client.request("GET", "/v1/payments", params={"limit": limit})

    def retrieve(self, payment_id: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/payments/{quote(payment_id, safe='')}")

    def events(self, payment_id: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/payments/{quote(payment_id, safe='')}/events")
