import json
from typing import Any, Dict, Optional
import urllib.request
import urllib.error
from urllib.parse import urlencode

from edpay.exceptions import EDPayException
from edpay.resources.payments import PaymentsResource
from edpay.resources.customers import CustomersResource
from edpay.resources.invoices import Invoices
from edpay.resources.subscriptions import Subscriptions
from edpay.resources.fx import FxResource
from edpay.resources.wallets import WalletsResource
from edpay.resources.webhooks import WebhooksResource
from edpay.resources.public import PublicResource


class EDPayClient:
    """Official client for interacting with the EDPay API."""

    DEFAULT_BASE_URL = "https://api-pay.edutecka.com"

    def __init__(
        self,
        public_key: str,
        private_key: str,
        base_url: Optional[str] = None,
        timeout: float = 90.0,
    ):
        public_key = public_key.strip() if isinstance(public_key, str) else ""
        private_key = private_key.strip() if isinstance(private_key, str) else ""
        public_mode = "test" if len(public_key) == 32 and public_key.startswith("pk_test_") else "live" if len(public_key) == 32 and public_key.startswith("pk_live_") else None
        private_mode = "test" if len(private_key) == 72 and private_key.startswith("sk_test_") else "live" if len(private_key) == 72 and private_key.startswith("sk_live_") else None
        if not public_mode or not all(char in "0123456789abcdefABCDEF" for char in public_key[8:]):
            public_mode = None
        if not private_mode or not all(char in "0123456789abcdefABCDEF" for char in private_key[8:]):
            private_mode = None
        if not public_mode or not private_mode:
            raise ValueError("EDPayClient requires a valid public_key (pk_test_/pk_live_ plus 24 hex characters) and private_key (sk_test_/sk_live_ plus 64 hex characters).")
        if public_mode != private_mode:
            raise ValueError("EDPay public_key and private_key must use the same environment (test or live).")

        self.public_key = public_key
        self.private_key = private_key
        self.timeout = timeout
        self.base_url = base_url.rstrip("/") if base_url else self.DEFAULT_BASE_URL

        # Resources
        self.payments = PaymentsResource(self)
        self.customers = CustomersResource(self)
        self.invoices = Invoices(self)
        self.subscriptions = Subscriptions(self)
        self.fx = FxResource(self)
        self.wallets = WalletsResource(self)
        self.webhooks = WebhooksResource(self)
        self.public = PublicResource(self)

    def request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        *,
        authenticated: bool = True,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute an authenticated HTTP request to the EDPay API."""
        if data is not None:
            if json_data is not None:
                raise ValueError("Pass either json_data or data, not both.")
            json_data = data
        url = f"{self.base_url}{endpoint}"
        if params:
            url += ("&" if "?" in url else "?") + urlencode(params, doseq=True)
        req_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "EDPay-Python-SDK/1.6.2",
        }
        if authenticated:
            req_headers["X-EDPay-Public-Key"] = self.public_key
            req_headers["X-EDPay-Private-Key"] = self.private_key
        if idempotency_key:
            req_headers["Idempotency-Key"] = idempotency_key
        if headers:
            req_headers.update(headers)

        body_bytes = None
        if json_data is not None:
            body_bytes = json.dumps(json_data).encode("utf-8")

        req = urllib.request.Request(url, data=body_bytes, headers=req_headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_bytes = resp.read()
                if not resp_bytes:
                    return {}
                return json.loads(resp_bytes.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
                api_error = err_json.get("error") or {}
                msg = api_error.get("message") if isinstance(api_error, dict) else api_error
                msg = msg or err_json.get("message") or "Unknown EDPay error"
            except Exception:
                err_json = {"raw": err_body}
                msg = f"HTTP {exc.code} error: {exc.reason}"
            api_error = err_json.get("error") if isinstance(err_json, dict) else None
            api_error = api_error if isinstance(api_error, dict) else {}
            raise EDPayException(
                msg, status_code=exc.code, response_data=err_json,
                error_code=api_error.get("code"),
                request_id=exc.headers.get("X-Request-Id") if exc.headers else None,
                retry_after=exc.headers.get("Retry-After") if exc.headers else None,
            ) from exc
        except urllib.error.URLError as exc:
            raise EDPayException(f"Connection failed: {str(exc.reason)}", status_code=0) from exc
