from typing import Any, Dict, Optional
from urllib.parse import quote


class CheckoutResource:
    def __init__(self, client):
        self._client = client

    def create_session(
        self,
        payment_link_id: str,
        idempotency_key: str,
        embed_origin: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a checkout session hosted by EDPay."""
        payload: Dict[str, Any] = {"payment_link_id": payment_link_id}
        if embed_origin:
            payload["embed_origin"] = embed_origin
        return self._client.request("POST", "/v1/checkout/sessions", json_data=payload, idempotency_key=idempotency_key)

    def retrieve_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieve the details and status of a checkout session."""
        return self._client.request("GET", f"/v1/checkout/sessions/{quote(session_id, safe='')}", authenticated=False)

    def get_payment_link(self, link_id: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/checkout/payment-links/{quote(link_id, safe='')}", authenticated=False)

    def frame_policy(self, token: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/checkout/sessions/{quote(token, safe='')}/frame-policy", authenticated=False)

    def create_session_payment(self, token: str, method: str, phone: str, idempotency_key: str) -> Dict[str, Any]:
        return self._client.request("POST", f"/v1/checkout/sessions/{quote(token, safe='')}/payments",
                                    json_data={"method": method, "phone": phone}, idempotency_key=idempotency_key, authenticated=False)

    def retrieve_session_payment(self, token: str, payment_id: str) -> Dict[str, Any]:
        path = f"/v1/checkout/sessions/{quote(token, safe='')}/payments/{quote(payment_id, safe='')}"
        return self._client.request("GET", path, authenticated=False)

    def create_payment_link_payment(self, link_id: str, method: str, phone: str, idempotency_key: str) -> Dict[str, Any]:
        return self._client.request("POST", f"/v1/checkout/payment-links/{quote(link_id, safe='')}/payments",
                                    json_data={"method": method, "phone": phone}, idempotency_key=idempotency_key, authenticated=False)

    def retrieve_payment_link_payment(self, link_id: str, payment_id: str) -> Dict[str, Any]:
        path = f"/v1/checkout/payment-links/{quote(link_id, safe='')}/payments/{quote(payment_id, safe='')}"
        return self._client.request("GET", path, authenticated=False)
