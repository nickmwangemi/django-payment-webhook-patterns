import json
import time

import pytest
from django.conf import settings

from webhooks.handlers.mollie import MollieWebhookHandler
from webhooks.stripe_signing import build_stripe_signature_header


@pytest.fixture
def stripe_secret():
    return settings.STRIPE_WEBHOOK_SECRET


@pytest.fixture
def mollie_secret():
    return settings.MOLLIE_WEBHOOK_SECRET


def stripe_event_payload(event_id: str = "evt_test_123") -> dict:
    return {
        "id": event_id,
        "object": "event",
        "type": "payment_intent.succeeded",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "pi_test_123",
                "object": "payment_intent",
                "status": "succeeded",
            }
        },
    }


def sign_stripe_payload(payload: dict, secret: str) -> tuple[bytes, str]:
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    signature = build_stripe_signature_header(raw.decode("utf-8"), secret)
    return raw, signature


def sign_mollie_body(body: bytes, secret: str) -> str:
    return MollieWebhookHandler(webhook_secret=secret).compute_signature(body)
