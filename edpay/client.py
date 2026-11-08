import json
from typing import Any, Dict, Optional
import urllib.request
import urllib.error

from edpay.exceptions import EDPayException
from edpay.resources.payments import PaymentsResource
from edpay.resources.checkout import CheckoutResource
from edpay.resources.payment_links import PaymentLinksResource
from edpay.resources.customers import CustomersResource
from edpay.resources.invoices import Invoices
from edpay.resources.subscriptions import Subscriptions


class EDPayClient:
    """Cliente oficial para interagir com a API EDPay."""

    DEFAULT_BASE_URL = "https://api.edpay.co.mz"
    SANDBOX_BASE_URL = "https://sandbox-api.edpay.co.mz"

    def __init__(
        self,
        public_key: str,
        private_key: str,
        environment: str = "production",
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        if not public_key or not private_key:
            raise ValueError("EDPayClient requer public_key e private_key válidas.")

        self.public_key = public_key
        self.private_key = private_key
        self.environment = environment
        self.timeout = timeout

        if base_url:
            self.base_url = base_url.rstrip("/")
        else:
            self.base_url = (
                self.SANDBOX_BASE_URL if environment.lower() in ("sandbox", "test") else self.DEFAULT_BASE_URL
            )

        # Recursos
        self.payments = PaymentsResource(self)
        self.checkout = CheckoutResource(self)
        self.payment_links = PaymentLinksResource(self)
        self.customers = CustomersResource(self)
        self.invoices = Invoices(self)
        self.subscriptions = Subscriptions(self)

    def request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Executa uma requisição HTTP autenticada à API EDPay."""
        url = f"{self.base_url}{endpoint}"
        req_headers = {
            "X-EDPay-Public-Key": self.public_key,
            "X-EDPay-Private-Key": self.private_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "EDPay-Python-SDK/1.0.0",
        }
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
                msg = err_json.get("message") or err_json.get("error") or "Unknown EDPay error"
            except Exception:
                err_json = {"raw": err_body}
                msg = f"HTTP {exc.code} error: {exc.reason}"
            raise EDPayException(msg, status_code=exc.code, response_data=err_json) from exc
        except urllib.error.URLError as exc:
            raise EDPayException(f"Connection failed: {str(exc.reason)}", status_code=0) from exc
