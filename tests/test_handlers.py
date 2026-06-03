import pytest

from webhooks.exceptions import InvalidSignatureError
from webhooks.handlers.mollie import MollieWebhookHandler
from webhooks.handlers.stripe import StripeWebhookHandler
from tests.conftest import sign_mollie_body, sign_stripe_payload, stripe_event_payload


def test_stripe_handler_parses_event(stripe_secret):
    payload = stripe_event_payload("evt_unit_1")
    raw, signature = sign_stripe_payload(payload, stripe_secret)

    result = StripeWebhookHandler(webhook_secret=stripe_secret).handle(
        raw_body=raw,
        signature_header=signature,
    )

    assert result.provider == "stripe"
    assert result.external_id == "evt_unit_1"
    assert result.event_type == "payment_intent.succeeded"


def test_mollie_handler_requires_signature(mollie_secret):
    handler = MollieWebhookHandler(webhook_secret=mollie_secret)

    with pytest.raises(InvalidSignatureError):
        handler.handle(raw_body=b"id=tr_1", signature_header=None)


def test_mollie_signature_roundtrip(mollie_secret):
    body = b"id=tr_roundtrip"
    signature = sign_mollie_body(body, mollie_secret)
    result = MollieWebhookHandler(webhook_secret=mollie_secret).handle(
        raw_body=body,
        signature_header=signature,
        content_type="application/x-www-form-urlencoded",
    )

    assert result.external_id == "payment_tr_roundtrip"
