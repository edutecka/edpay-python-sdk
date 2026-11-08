from typing import Any, Dict, Optional


class CustomersResource:
    def __init__(self, client):
        self._client = client

    def create(
        self,
        name: str,
        email: str,
        phone: Optional[str] = None,
        tax_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Cria um cliente no sistema EDPay."""
        payload: Dict[str, Any] = {
            "name": name,
            "email": email,
        }
        if phone:
            payload["phone"] = phone
        if tax_id:
            payload["tax_id"] = tax_id
        if metadata:
            payload["metadata"] = metadata

        return self._client.request("POST", "/v1/customers", json_data=payload)

    def retrieve(self, customer_id: str) -> Dict[str, Any]:
        """Consulta um cliente pelo ID."""
        return self._client.request("GET", f"/v1/customers/{customer_id}")

    def update(self, customer_id: str, **kwargs) -> Dict[str, Any]:
        """Atualiza os dados de um cliente."""
        return self._client.request("PUT", f"/v1/customers/{customer_id}", json_data=kwargs)
