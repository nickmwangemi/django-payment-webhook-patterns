import hashlib
import hmac
import json
from typing import Any
from urllib.parse import parse_qs

from django.conf import settings

from webhooks.exceptions import InvalidPayloadError, InvalidSignatureError
from webhooks.handlers.base import WebhookResult


class MollieWebhookHandler:
    """
    Handle Mollie-style webhooks.

    Production Mollie often notifies with a payment id; apps re-fetch status via API.
    This demo adds an HMAC signature header so tests can verify authenticity without
    calling external services.
    """

    PROVIDER = "mollie"
    SIGNATURE_HEADER = "X-Mollie-Signature"

    def __init__(self, webhook_secret: str | None = None):
        self.webhook_secret = webhook_secret or settings.MOLLIE_WEBHOOK_SECRET

    def compute_signature(self, body: bytes) -> str:
        digest = hmac.new(
            self.webhook_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
        return f"sha256={digest}"

    def verify_signature(self, raw_body: bytes, signature_header: str | None) -> None:
        if not signature_header:
            raise InvalidSignatureError("Missing X-Mollie-Signature header")

        expected = self.compute_signature(raw_body)
        if not hmac.compare_digest(expected, signature_header):
            raise InvalidSignatureError("Mollie signature mismatch")

    def parse_body(self, raw_body: bytes, content_type: str) -> dict[str, Any]:
        if not raw_body:
            raise InvalidPayloadError("Empty webhook body")

        if "application/json" in content_type:
            try:
                return json.loads(raw_body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise InvalidPayloadError(str(exc)) from exc

        # Mollie commonly posts application/x-www-form-urlencoded with an id field.
        parsed = parse_qs(raw_body.decode("utf-8"))
        payment_id = (parsed.get("id") or [None])[0]
        if not payment_id:
            raise InvalidPayloadError("Mollie webhook missing payment id")

        return {
            "id": payment_id,
            "resource": (parsed.get("resource") or ["payment"])[0],
        }

    def handle(
        self,
        raw_body: bytes,
        signature_header: str | None,
        content_type: str = "",
    ) -> WebhookResult:
        self.verify_signature(raw_body, signature_header)
        payload = self.parse_body(raw_body, content_type)
        payment_id = payload["id"]

        return WebhookResult(
            provider=self.PROVIDER,
            external_id=f"payment_{payment_id}",
            event_type=f"payment.{payload.get('resource', 'payment')}",
            payload=payload,
        )
