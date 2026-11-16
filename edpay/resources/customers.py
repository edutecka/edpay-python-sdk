from typing import Any, Dict, Optional
from urllib.parse import quote


class CustomersResource:
    def __init__(self, client):
        self._client = client

    def create(
        self,
        name: str,
        email: Optional[str] = None,
        *,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """Create a customer in the EDPay system."""
        payload: Dict[str, Any] = {
            "name": name,
            "email": email,
        }
        return self._client.request("POST", "/v1/customers", json_data=payload, idempotency_key=idempotency_key)

    def list(self) -> Dict[str, Any]:
        return self._client.request("GET", "/v1/customers")

    def retrieve(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve a customer by ID."""
        return self._client.request("GET", f"/v1/customers/{quote(customer_id, safe='')}")

    def update(self, customer_id: str, *, idempotency_key: str, **fields: Any) -> Dict[str, Any]:
        """Patch customer name/email; an idempotency key is mandatory."""
        return self._client.request("PATCH", f"/v1/customers/{quote(customer_id, safe='')}", json_data=fields, idempotency_key=idempotency_key)
