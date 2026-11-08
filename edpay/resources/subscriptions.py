from typing import Any, Dict, Optional


class Subscriptions:
    """Recurso para criação e gestão de planos de faturação recorrente / subscrições."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def create(
        self,
        params: Dict[str, Any],
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cria uma série de subscrição recorrente (invoice series)."""
        return self._client.request("POST", "/v1/invoice-series", data=params, idempotency_key=idempotency_key)

    def get(self, series_id: str) -> Dict[str, Any]:
        """Consulta os dados de uma subscrição por ID."""
        return self._client.request("GET", f"/v1/invoice-series/{series_id}")

    def list(self, **params: Any) -> Dict[str, Any]:
        """Lista subscrições com filtros opcionais."""
        return self._client.request("GET", "/v1/invoice-series", params=params)

    def pause(self, series_id: str) -> Dict[str, Any]:
        """Pausa uma subscrição recorrente."""
        return self._client.request("POST", f"/v1/invoice-series/{series_id}/pause")

    def resume(self, series_id: str) -> Dict[str, Any]:
        """Retoma uma subscrição pausada."""
        return self._client.request("POST", f"/v1/invoice-series/{series_id}/resume")
