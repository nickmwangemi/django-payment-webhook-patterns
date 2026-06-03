from django.db import IntegrityError, transaction

from webhooks.exceptions import DuplicateEventError
from webhooks.handlers.base import WebhookResult
from webhooks.models import WebhookEvent


def persist_webhook_event(result: WebhookResult) -> WebhookResult:
    """Store the event once; return result with duplicate=True if already seen."""
    try:
        with transaction.atomic():
            WebhookEvent.objects.create(
                provider=result.provider,
                external_id=result.external_id,
                event_type=result.event_type,
                payload=result.payload,
            )
    except IntegrityError:
        return WebhookResult(
            provider=result.provider,
            external_id=result.external_id,
            event_type=result.event_type,
            payload=result.payload,
            duplicate=True,
        )

    return result


def process_webhook(result: WebhookResult) -> WebhookResult:
    """
    Demo business hook: in a real app you would update payment state here.
    This portfolio repo only records idempotent webhook events.
    """
    if result.duplicate:
        raise DuplicateEventError(
            f"{result.provider} event {result.external_id} already processed"
        )
    return result
