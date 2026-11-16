from typing import Any, Dict, Optional
from urllib.parse import quote


class WebhooksResource:
    def __init__(self, client: Any) -> None:
        self._client = client

    def list_endpoints(self) -> Dict[str, Any]:
        return self._client.request("GET", "/v1/webhook-endpoints")

    def create_endpoint(self, payload: Dict[str, Any], idempotency_key: str) -> Dict[str, Any]:
        return self._client.request("POST", "/v1/webhook-endpoints", json_data=payload, idempotency_key=idempotency_key)

    def update_endpoint(self, endpoint_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._client.request("PATCH", f"/v1/webhook-endpoints/{quote(endpoint_id, safe='')}", json_data=payload)

    def disable_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        return self._client.request("POST", f"/v1/webhook-endpoints/{quote(endpoint_id, safe='')}/disable")

    def delete_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        return self._client.request("DELETE", f"/v1/webhook-endpoints/{quote(endpoint_id, safe='')}")

    def list_deliveries(self, limit: Optional[int] = None) -> Dict[str, Any]:
        params = {"limit": limit} if limit is not None else None
        return self._client.request("GET", "/v1/webhook-deliveries", params=params)

    def retrieve_delivery(self, delivery_id: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/webhook-deliveries/{quote(delivery_id, safe='')}")

    def retry_delivery(self, delivery_id: str) -> Dict[str, Any]:
        return self._client.request("POST", f"/v1/webhook-deliveries/{quote(delivery_id, safe='')}/retry")
