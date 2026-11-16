"""Exceptions for the EDPay Python SDK."""


class EDPayException(Exception):
    """Base exception for EDPay API errors."""

    def __init__(self, message: str, status_code: int = 400, response_data: dict = None,
                 error_code: str = None, request_id: str = None, retry_after: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.error_code = error_code
        self.request_id = request_id
        self.retry_after = retry_after

    def __str__(self):
        return f"[EDPay Error {self.status_code}] {self.message}"


class SignatureVerificationException(EDPayException):
    """Raised when an HMAC SHA-256 webhook signature is invalid."""

    def __init__(self, message: str = "Invalid EDPay webhook signature"):
        super().__init__(message, status_code=400)
