"""Utilitários de segurança para verificação de assinaturas de Webhook."""

import hmac
import hashlib


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verifica se a assinatura recebida no header `X-EDPay-Signature` é autêntica.
    Usa comparação em tempo constante contra ataques de timing (HMAC SHA-256).
    """
    if not payload or not signature or not secret:
        return False

    computed = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed.lower(), signature.strip().lower())
