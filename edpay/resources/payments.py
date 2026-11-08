from typing import Any, Dict, Optional


class PaymentsResource:
    def __init__(self, client):
        self._client = client

    def create(
        self,
        amount_minor: int,
        currency: str,
        method: str,
        phone: Optional[str] = None,
        reference: Optional[str] = None,
        description: Optional[str] = None,
        emola_custom_message: Optional[str] = None,
        customer: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cria uma transação de pagamento direta na EDPay."""
        payload: Dict[str, Any] = {
            "amount_minor": amount_minor,
            "currency": currency,
            "method": method,
        }
        if phone:
            payload["phone"] = phone
        if reference:
            payload["reference"] = reference
        if description:
            payload["description"] = description
        if emola_custom_message:
            payload["emola_custom_message"] = emola_custom_message
        if customer:
            payload["customer"] = customer
        if metadata:
            payload["metadata"] = metadata

        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        return self._client.request("POST", "/v1/payments", json_data=payload, headers=headers)

    def retrieve(self, payment_id: str) -> Dict[str, Any]:
        """Consulta o estado de um pagamento pelo seu identificador único."""
        return self._client.request("GET", f"/v1/payments/{payment_id}")

    def cancel(self, payment_id: str) -> Dict[str, Any]:
        """Cancela um pagamento pendente."""
        return self._client.request("POST", f"/v1/payments/{payment_id}/cancel")
