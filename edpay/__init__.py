"""EDPay Python SDK"""
__version__ = "0.1.0"

class EDPayClient:
    def __init__(self, public_key: str, private_key: str, base_url: str = "https://api-pay.edutecka.com"):
        self.public_key = public_key
        self.private_key = private_key
        self.base_url = base_url.rstrip("/")
