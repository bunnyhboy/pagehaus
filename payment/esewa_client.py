import base64
import hashlib
import hmac
import json

import requests
from django.conf import settings


class EsewaClient:
    """
    Wraps eSewa's ePay v2 API. Every environment-specific value comes from
    Django settings — switching from test to production credentials is a
    settings/env var change only, nothing here needs to change.
    """

    def __init__(self):
        self.product_code = settings.ESEWA_PRODUCT_CODE
        self.secret_key = settings.ESEWA_SECRET_KEY
        self.payment_url = settings.ESEWA_PAYMENT_URL
        self.status_check_url = settings.ESEWA_STATUS_CHECK_URL
        self.success_url = settings.ESEWA_SUCCESS_URL
        self.failure_url = settings.ESEWA_FAILURE_URL

    def _sign(self, message: str) -> str:
        digest = hmac.new(
            self.secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return base64.b64encode(digest).decode("utf-8")

    def build_form_payload(self, *, amount, transaction_uuid):
        """
        Field dict the frontend should POST (as a hidden auto-submit form)
        to self.payment_url. eSewa requires an actual form POST, not just
        a redirect link.
        """

        total_amount = f"{amount:.2f}"
        signed_field_names = "total_amount,transaction_uuid,product_code"

        signature_message = (
            f"total_amount={total_amount},"
            f"transaction_uuid={transaction_uuid},"
            f"product_code={self.product_code}"
        )

        return {
            "amount": total_amount,
            "tax_amount": "0",
            "total_amount": total_amount,
            "transaction_uuid": str(transaction_uuid),
            "product_code": self.product_code,
            "product_service_charge": "0",
            "product_delivery_charge": "0",
            "success_url": self.success_url,
            # transaction_uuid appended so the failure handler knows which
            # payment failed — eSewa's failure redirect carries no other info.
            "failure_url": f"{self.failure_url}?transaction_uuid={transaction_uuid}",
            "signed_field_names": signed_field_names,
            "signature": self._sign(signature_message),
        }

    def decode_response(self, encoded_data: str) -> dict:
        """eSewa redirects to success_url?data=<base64 JSON>."""
        decoded = base64.b64decode(encoded_data).decode("utf-8")
        return json.loads(decoded)

    def verify_response_signature(self, data: dict) -> bool:
        signed_field_names = data.get("signed_field_names", "")
        fields = signed_field_names.split(",")

        message = ",".join(f"{field}={data.get(field, '')}" for field in fields)
        expected_signature = self._sign(message)

        return hmac.compare_digest(expected_signature, data.get("signature", ""))

    def check_transaction_status(self, *, amount, transaction_uuid):
        """
        Server-to-server verification — always call before trusting a
        success redirect, since redirect query params can be spoofed.
        """
        params = {
            "product_code": self.product_code,
            "total_amount": f"{amount:.2f}",
            "transaction_uuid": str(transaction_uuid),
        }

        response = requests.get(self.status_check_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()