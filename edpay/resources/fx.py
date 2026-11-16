from typing import Any, Dict


class FxResource:
    def __init__(self, client: Any) -> None:
        self._client = client

    def quote(self, from_currency: str, to_currency: str, amount_minor: int) -> Dict[str, Any]:
        return self._client.request(
            "GET",
            "/v1/fx/quote",
            params={"from_currency": from_currency, "to_currency": to_currency, "amount_minor": amount_minor},
        )
