from typing import Any, Dict, Optional
from urllib.parse import quote


class WalletsResource:
    def __init__(self, client: Any) -> None:
        self._client = client

    def list(self) -> Dict[str, Any]:
        return self._client.request("GET", "/v1/wallets")

    def retrieve(self, wallet_id: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/wallets/{quote(wallet_id, safe='')}")

    def balance(self, wallet_id: str) -> Dict[str, Any]:
        return self._client.request("GET", f"/v1/wallets/{quote(wallet_id, safe='')}/balance")

    def entries(self, wallet_id: str, cursor: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        params = {key: value for key, value in {"cursor": cursor, "limit": limit}.items() if value is not None}
        return self._client.request("GET", f"/v1/wallets/{quote(wallet_id, safe='')}/entries", params=params)
