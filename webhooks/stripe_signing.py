"""Helpers for Stripe webhook signature verification and test signing."""

import hashlib
import hmac
import time


def build_stripe_signature_header(payload: str, secret: str, timestamp: int | None = None) -> str:
    """
    Build a Stripe-Signature header value for tests and local tooling.

    Matches stripe-python WebhookSignature._compute_signature (secret as UTF-8).
    """
    ts = timestamp if timestamp is not None else int(time.time())
    signed_payload = f"{ts}.{payload}"
    digest = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"t={ts},v1={digest}"
