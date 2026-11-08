"""EDPay Python SDK - Biblioteca oficial de pagamentos."""

from edpay.client import EDPayClient
from edpay.exceptions import EDPayException, SignatureVerificationException
from edpay.webhooks import verify_webhook_signature

__version__ = "1.0.0"
__all__ = [
    "EDPayClient",
    "EDPayException",
    "SignatureVerificationException",
    "verify_webhook_signature",
]
