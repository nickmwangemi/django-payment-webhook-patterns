import json

import pytest
from django.urls import reverse

from tests.conftest import sign_mollie_body
from webhooks.models import WebhookEvent


@pytest.mark.django_db
class TestMollieWebhookView:
    url = reverse("mollie-webhook")

    def test_accepts_form_encoded_payment_id(self, client, mollie_secret):
        body = b"id=tr_synthetic_abc&resource=payment"
        signature = sign_mollie_body(body, mollie_secret)

        response = client.post(
            self.url,
            data=body,
            content_type="application/x-www-form-urlencoded",
            HTTP_X_MOLLIE_SIGNATURE=signature,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["provider"] == "mollie"
        assert data["external_id"] == "payment_tr_synthetic_abc"
        assert WebhookEvent.objects.filter(provider="mollie").count() == 1

    def test_accepts_json_payload(self, client, mollie_secret):
        payload = {"id": "tr_json_99", "resource": "payment"}
        body = json.dumps(payload).encode("utf-8")
        signature = sign_mollie_body(body, mollie_secret)

        response = client.post(
            self.url,
            data=body,
            content_type="application/json",
            HTTP_X_MOLLIE_SIGNATURE=signature,
        )

        assert response.status_code == 200
        assert response.json()["external_id"] == "payment_tr_json_99"

    def test_rejects_invalid_signature(self, client, mollie_secret):
        body = b"id=tr_bad_sig"

        response = client.post(
            self.url,
            data=body,
            content_type="application/x-www-form-urlencoded",
            HTTP_X_MOLLIE_SIGNATURE="sha256=deadbeef",
        )

        assert response.status_code == 401
        assert WebhookEvent.objects.count() == 0

    def test_duplicate_event_is_idempotent(self, client, mollie_secret):
        body = b"id=tr_dup_1&resource=payment"
        signature = sign_mollie_body(body, mollie_secret)
        headers = {"HTTP_X_MOLLIE_SIGNATURE": signature}

        first = client.post(
            self.url,
            data=body,
            content_type="application/x-www-form-urlencoded",
            **headers,
        )
        second = client.post(
            self.url,
            data=body,
            content_type="application/x-www-form-urlencoded",
            **headers,
        )

        assert first.json()["status"] == "ok"
        assert second.json()["status"] == "duplicate"
        assert WebhookEvent.objects.count() == 1

    def test_rejects_missing_payment_id(self, client, mollie_secret):
        body = b"resource=payment"
        signature = sign_mollie_body(body, mollie_secret)

        response = client.post(
            self.url,
            data=body,
            content_type="application/x-www-form-urlencoded",
            HTTP_X_MOLLIE_SIGNATURE=signature,
        )

        assert response.status_code == 400
