from typing import Any, Dict, Optional


class Invoices:
    """Recurso para criação, consulta e finalização de faturas."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def create(
        self,
        params: Dict[str, Any],
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cria uma fatura comercial com itens e prazos de vencimento."""
        return self._client.request("POST", "/v1/invoices", data=params, idempotency_key=idempotency_key)

    def get(self, invoice_id: str) -> Dict[str, Any]:
        """Consulta os dados de uma fatura por ID."""
        return self._client.request("GET", f"/v1/invoices/{invoice_id}")

    def list(self, **params: Any) -> Dict[str, Any]:
        """Lista faturas com filtros opcionais."""
        return self._client.request("GET", "/v1/invoices", params=params)

    def finalize(
        self,
        invoice_id: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Finaliza e emite a fatura, gerando a URL de checkout."""
        return self._client.request("POST", f"/v1/invoices/{invoice_id}/finalize", idempotency_key=idempotency_key)

    def void(self, invoice_id: str) -> Dict[str, Any]:
        """Anula uma fatura emitida."""
        return self._client.request("POST", f"/v1/invoices/{invoice_id}/void")
