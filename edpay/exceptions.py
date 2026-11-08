"""Exceções do EDPay Python SDK."""


class EDPayException(Exception):
    """Exceção base para erros na API EDPay."""

    def __init__(self, message: str, status_code: int = 400, response_data: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self):
        return f"[EDPay Error {self.status_code}] {self.message}"


class SignatureVerificationException(EDPayException):
    """Lançada quando a assinatura de um webhook HMAC SHA-256 for inválida."""

    def __init__(self, message: str = "Invalid EDPay webhook signature"):
        super().__init__(message, status_code=400)
