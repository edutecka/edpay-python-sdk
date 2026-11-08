from typing import Any, Dict, List, Optional


class PaymentLinksResource:
    def __init__(self, client):
        self._client = client

    def create(
        self,
        title: str,
        amount_minor: int,
        currency: str = "MZN",
        description: Optional[str] = None,
        allowed_methods: Optional[List[str]] = None,
        max_uses: Optional[int] = None,
        expires_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cria um link de pagamento partilhável."""
        payload: Dict[str, Any] = {
            "title": title,
            "amount_minor": amount_minor,
            "currency": currency,
        }
        if description:
            payload["description"] = description
        if allowed_methods:
            payload["allowed_methods"] = allowed_methods
        if max_uses is not None:
            payload["max_uses"] = max_uses
        if expires_at:
            payload["expires_at"] = expires_at
        if metadata:
            payload["metadata"] = metadata

        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        return self._client.request("POST", "/v1/payment-links", json_data=payload, headers=headers)

    def retrieve(self, link_id: str) -> Dict[str, Any]:
        """Consulta os dados de um link de pagamento."""
        return self._client.request("GET", f"/v1/payment-links/{link_id}")

    def revoke(self, link_id: str) -> Dict[str, Any]:
        """Revoga ou desativa um link de pagamento."""
        return self._client.request("POST", f"/v1/payment-links/{link_id}/revoke")
