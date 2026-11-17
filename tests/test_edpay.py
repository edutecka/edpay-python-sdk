import unittest
import hashlib
import hmac
import time
from edpay.webhooks import verify_webhook_signature
from edpay.exceptions import EDPayException


class TestEDPay(unittest.TestCase):
    def test_webhook_signature_verification(self):
        payload = b'{"event":"payment.succeeded","data":{"id":"pay_123"}}'
        secret = "whsec_test_secret_key"
        timestamp = int(time.time())
        signed_payload = str(timestamp).encode("ascii") + b"." + payload
        signature = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
        signature_header = f"t={timestamp},v1={signature}"

        self.assertTrue(verify_webhook_signature(payload, signature_header, secret))
        self.assertFalse(verify_webhook_signature(payload, "t=invalid,v1=invalid", secret))
        self.assertFalse(verify_webhook_signature(b"other", signature_header, secret))


if __name__ == "__main__":
    unittest.main()
