import json
from typing import Any

import stripe
from django.conf import settings

from webhooks.exceptions import InvalidPayloadError, InvalidSignatureError
from webhooks.handlers.base import WebhookResult


class StripeWebhookHandler:
    """Verify and parse synthetic Stripe webhook events."""

    PROVIDER = "stripe"

    def __init__(self, webhook_secret: str | None = None):
        self.webhook_secret = webhook_secret or settings.STRIPE_WEBHOOK_SECRET

    def verify_and_parse(
        self, raw_body: bytes, signature_header: str | None
    ) -> dict[str, Any]:
        if not signature_header:
            raise InvalidSignatureError("Missing Stripe-Signature header")

        try:
            stripe.Webhook.construct_event(
                payload=raw_body,
                sig_header=signature_header,
                secret=self.webhook_secret,
            )
        except stripe.error.SignatureVerificationError as exc:
            raise InvalidSignatureError(str(exc)) from exc
        except ValueError as exc:
            raise InvalidPayloadError(str(exc)) from exc

        try:
            return json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InvalidPayloadError(str(exc)) from exc

    def handle(self, raw_body: bytes, signature_header: str | None) -> WebhookResult:
        event = self.verify_and_parse(raw_body, signature_header)
        event_type = event.get("type", "unknown")
        external_id = event.get("id", "")

        if not external_id:
            raise InvalidPayloadError("Stripe event missing id")

        return WebhookResult(
            provider=self.PROVIDER,
            external_id=external_id,
            event_type=event_type,
            payload=event,
        )
