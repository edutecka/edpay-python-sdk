from typing import Any, Dict, Optional


class PaymentLinksResource:
    def __init__(self, client):
        self._client = client

    def create(
        self,
        amount_minor: int,
        currency: str,
        *,
        expires_at: Optional[str] = None,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """Create a shareable payment link."""
        payload: Dict[str, Any] = {
            "amount_minor": amount_minor,
            "currency": currency,
        }
        if expires_at:
            payload["expires_at"] = expires_at
        return self._client.request("POST", "/v1/payment-links", json_data=payload, idempotency_key=idempotency_key)

    def list(self) -> Dict[str, Any]:
        return self._client.request("GET", "/v1/payment-links")

    def retrieve(self, link_id: str) -> Dict[str, Any]:
        """Retrieve payment link data."""
        from urllib.parse import quote
        return self._client.request("GET", f"/v1/payment-links/{quote(link_id, safe='')}")

    def deactivate(self, link_id: str, *, idempotency_key: str) -> Dict[str, Any]:
        from urllib.parse import quote
        return self._client.request("POST", f"/v1/payment-links/{quote(link_id, safe='')}/deactivate", idempotency_key=idempotency_key)
