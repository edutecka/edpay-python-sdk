import unittest
from edpay.webhooks import verify_webhook_signature
from edpay.exceptions import EDPayException


class TestEDPay(unittest.TestCase):
    def test_webhook_signature_verification(self):
        payload = b'{"event":"payment.succeeded","data":{"id":"pay_123"}}'
        secret = "whsec_test_secret_key"
        
        # Correct HMAC SHA-256 for this payload and secret
        import hmac, hashlib
        sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        self.assertTrue(verify_webhook_signature(payload, sig, secret))
        self.assertFalse(verify_webhook_signature(payload, "invalid_sig", secret))
        self.assertFalse(verify_webhook_signature(b'other', sig, secret))


if __name__ == "__main__":
    unittest.main()
