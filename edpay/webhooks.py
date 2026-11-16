"""Security utilities for verifying EDPay webhook signatures."""

import hashlib
import hmac
import re
import time
from typing import Literal, Optional, TypedDict


EDPayWebhookEventType = Literal[
    "payment.created", "payment.updated", "payment.succeeded",
    "payment.failed", "payment.cancelled", "payment.reconciliation_required",
]
EDPayPaymentStatus = Literal["pending", "processing", "unknown", "succeeded", "failed", "cancelled"]


class EDPayWebhookPaymentData(TypedDict, total=False):
    """Sanitized payment data delivered in a payment webhook event."""
    object: Literal["payment"]
    id: str
    reference: str
    payment_link_id: Optional[str]
    trans_id: str
    method: str
    status: EDPayPaymentStatus
    amount_minor: int
    currency: Literal["MZN", "USD", "EUR"]
    platform_fee_minor: int
    receiver_net_minor: int
    reconciliation_status: Literal["manual_review"]
    reconciliation_code: str
    created_at: str


class EDPayWebhookEvent(TypedDict, total=False):
    """Verified webhook event envelope; verify signatures before parsing JSON."""
    id: str
    object: Literal["event"]
    type: EDPayWebhookEventType
    created_at: str
    data: EDPayWebhookPaymentData


def verify_webhook_signature(
    payload: bytes,
    signature_header: str,
    secret: str,
    *,
    tolerance_seconds: int = 300,
    now: Optional[int] = None,
) -> bool:
    """Verify a ``Payment-Signature`` header over the unmodified request body.

    EDPay signs ``timestamp + b"." + payload`` with HMAC-SHA256. Timestamps
    outside the default five-minute window are rejected to limit replay attacks.
    ``now`` is injectable for deterministic verification.
    """
    if not payload or not signature_header or not secret or tolerance_seconds < 0:
        return False

    timestamp = None
    signature = None
    for field in signature_header.split(","):
        key, separator, value = field.strip().partition("=")
        if not separator:
            continue
        if key == "t":
            if timestamp is not None:
                return False
            timestamp = value.strip()
        elif key == "v1":
            if signature is not None:
                return False
            signature = value.strip()

    if not timestamp or not re.fullmatch(r"\d+", timestamp):
        return False
    if not signature or not re.fullmatch(r"[0-9a-fA-F]{64}", signature):
        return False

    signed_at = int(timestamp)
    current_time = int(time.time()) if now is None else now
    if abs(current_time - signed_at) > tolerance_seconds:
        return False

    signed_payload = timestamp.encode("ascii") + b"." + payload
    expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).digest()
    try:
        received = bytes.fromhex(signature)
    except ValueError:
        return False
    return hmac.compare_digest(expected, received)
