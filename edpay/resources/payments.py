from typing import Any, Dict, Optional


class PaymentsResource:
    def __init__(self, client):
        self._client = client

    def create(
        self,
        amount_minor: int,
        currency: str,
        method: Optional[str] = None,
        methods: Optional[list] = None,
        phone: Optional[str] = None,
        reference: Optional[str] = None,
        description: Optional[str] = None,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        channel: Optional[str] = None,
        expires_in_minutes: Optional[int] = None,
        emola_custom_message: Optional[str] = None,
        customer: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cria uma transação de pagamento direta ou sessão de checkout unificada na EDPay."""
        payload: Dict[str, Any] = {
            "amount_minor": amount_minor,
            "currency": currency,
        }
        if method:
            payload["method"] = method
        if methods:
            payload["methods"] = methods
        if phone:
            payload["phone"] = phone
        if reference:
            payload["reference"] = reference
        if description:
            payload["description"] = description
        if return_url:
            payload["return_url"] = return_url
        if cancel_url:
            payload["cancel_url"] = cancel_url
        if channel:
            payload["channel"] = channel
        if expires_in_minutes:
            payload["expires_in_minutes"] = expires_in_minutes
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
