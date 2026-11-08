from typing import Any, Dict, List, Optional


class CheckoutResource:
    def __init__(self, client):
        self._client = client

    def create_session(
        self,
        amount_minor: int,
        currency: str,
        success_url: str,
        cancel_url: str,
        reference: Optional[str] = None,
        payment_methods: Optional[List[str]] = None,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cria uma sessão de checkout alojada pela EDPay."""
        payload: Dict[str, Any] = {
            "amount_minor": amount_minor,
            "currency": currency,
            "success_url": success_url,
            "cancel_url": cancel_url,
        }
        if reference:
            payload["reference"] = reference
        if payment_methods:
            payload["payment_methods"] = payment_methods
        if customer_email:
            payload["customer_email"] = customer_email
        if metadata:
            payload["metadata"] = metadata

        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        return self._client.request("POST", "/v1/checkout/sessions", json_data=payload, headers=headers)

    def retrieve_session(self, session_id: str) -> Dict[str, Any]:
        """Consulta os detalhes e o estado de uma sessão de checkout."""
        return self._client.request("GET", f"/v1/checkout/sessions/{session_id}")

    def expire_session(self, session_id: str) -> Dict[str, Any]:
        """Expira imediatamente uma sessão de checkout pendente."""
        return self._client.request("POST", f"/v1/checkout/sessions/{session_id}/expire")
