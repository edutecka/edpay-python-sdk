from typing import Any, Dict, Optional
from urllib.parse import quote


class Invoices:
    """Resource for creating, retrieving, and finalizing invoices."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def create(
        self,
        params: Dict[str, Any],
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """Create a commercial invoice with items and due dates."""
        return self._client.request("POST", "/v1/invoices", data=params, idempotency_key=idempotency_key)

    def get(self, invoice_id: str) -> Dict[str, Any]:
        """Retrieve invoice data by ID."""
        return self._client.request("GET", f"/v1/invoices/{quote(invoice_id, safe='')}")

    def list(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """List invoices, optionally limiting the number returned."""
        return self._client.request("GET", "/v1/invoices", params={"limit": limit} if limit is not None else None)

    def finalize(
        self,
        invoice_id: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Finalize and issue the invoice, generating the checkout URL."""
        return self._client.request("POST", f"/v1/invoices/{quote(invoice_id, safe='')}/finalize", idempotency_key=idempotency_key)

    def void(self, invoice_id: str) -> Dict[str, Any]:
        """Void an issued invoice."""
        return self._client.request("POST", f"/v1/invoices/{quote(invoice_id, safe='')}/void")
