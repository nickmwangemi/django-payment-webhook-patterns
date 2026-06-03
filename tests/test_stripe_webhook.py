import json

import pytest
from django.urls import reverse

from tests.conftest import sign_stripe_payload, stripe_event_payload
from webhooks.models import WebhookEvent


@pytest.mark.django_db
class TestStripeWebhookView:
    url = reverse("stripe-webhook")

    def test_accepts_valid_signed_event(self, client, stripe_secret):
        payload = stripe_event_payload()
        raw, signature = sign_stripe_payload(payload, stripe_secret)

        response = client.post(
            self.url,
            data=raw,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=signature,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["provider"] == "stripe"
        assert body["external_id"] == payload["id"]
        assert WebhookEvent.objects.filter(provider="stripe").count() == 1

    def test_rejects_missing_signature(self, client, stripe_secret):
        payload = stripe_event_payload("evt_missing_sig")
        raw, _ = sign_stripe_payload(payload, stripe_secret)

        response = client.post(
            self.url,
            data=raw,
            content_type="application/json",
        )

        assert response.status_code == 401
        assert WebhookEvent.objects.count() == 0

    def test_rejects_invalid_signature(self, client, stripe_secret):
        payload = stripe_event_payload("evt_bad_sig")
        raw, _ = sign_stripe_payload(payload, stripe_secret)

        response = client.post(
            self.url,
            data=raw,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=0,v1=invalid",
        )

        assert response.status_code == 401

    def test_duplicate_event_is_idempotent(self, client, stripe_secret):
        payload = stripe_event_payload("evt_duplicate_1")
        raw, signature = sign_stripe_payload(payload, stripe_secret)
        headers = {"HTTP_STRIPE_SIGNATURE": signature}

        first = client.post(
            self.url, data=raw, content_type="application/json", **headers
        )
        second = client.post(
            self.url, data=raw, content_type="application/json", **headers
        )

        assert first.status_code == 200
        assert first.json()["status"] == "ok"
        assert second.status_code == 200
        assert second.json()["status"] == "duplicate"
        assert WebhookEvent.objects.filter(external_id=payload["id"]).count() == 1

    def test_rejects_invalid_json(self, client, stripe_secret):
        from webhooks.stripe_signing import build_stripe_signature_header

        raw = b"not-json"
        signature = build_stripe_signature_header(raw.decode("utf-8"), stripe_secret)

        response = client.post(
            self.url,
            data=raw,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=signature,
        )

        assert response.status_code == 400
