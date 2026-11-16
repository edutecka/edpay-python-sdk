from typing import Any, Dict, Optional
from urllib.parse import quote


class Subscriptions:
    """Resource for creating and managing recurring billing plans / subscriptions."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def create(
        self,
        params: Dict[str, Any],
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """Create a recurring subscription series (invoice series)."""
        return self._client.request("POST", "/v1/invoice-series", data=params, idempotency_key=idempotency_key)

    def list(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """List invoice series, optionally limiting the number returned."""
        return self._client.request("GET", "/v1/invoice-series", params={"limit": limit} if limit is not None else None)

    def pause(self, series_id: str) -> Dict[str, Any]:
        """Pause a recurring subscription."""
        return self._client.request("POST", f"/v1/invoice-series/{quote(series_id, safe='')}/pause")

    def resume(self, series_id: str) -> Dict[str, Any]:
        """Resume a paused subscription."""
        return self._client.request("POST", f"/v1/invoice-series/{quote(series_id, safe='')}/resume")
