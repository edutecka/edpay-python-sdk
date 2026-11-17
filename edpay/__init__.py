"""EDPay Python SDK - Official payment library."""

from edpay.client import EDPayClient
from edpay.exceptions import EDPayException, SignatureVerificationException
from edpay.webhooks import verify_webhook_signature
from edpay.contacts import (
    add_country_prefix,
    format_phone_number,
    normalize_phone_number,
    phone_number_options_for_method,
    remove_country_prefix,
    validate_phone_number,
)
from edpay.webhooks import EDPayWebhookEvent, EDPayWebhookEventType, EDPayWebhookPaymentData, EDPayPaymentStatus

__version__ = "1.6.1"
__all__ = [
    "EDPayClient",
    "EDPayException",
    "SignatureVerificationException",
    "verify_webhook_signature",
    "add_country_prefix",
    "format_phone_number",
    "normalize_phone_number",
    "phone_number_options_for_method",
    "remove_country_prefix",
    "validate_phone_number",
    "EDPayWebhookEvent",
    "EDPayWebhookEventType",
    "EDPayWebhookPaymentData",
    "EDPayPaymentStatus",
]
