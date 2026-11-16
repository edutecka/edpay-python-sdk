from typing import Any, Dict


class PublicResource:
    def __init__(self, client: Any) -> None:
        self._client = client

    def list_payment_methods(self) -> Dict[str, Any]:
        return self._client.request("GET", "/v1/public/payment-methods", authenticated=False)
