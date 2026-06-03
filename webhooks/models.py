from django.db import models


class WebhookEvent(models.Model):
    """Idempotent record of a processed provider webhook."""

    PROVIDER_STRIPE = "stripe"
    PROVIDER_MOLLIE = "mollie"
    PROVIDER_CHOICES = [
        (PROVIDER_STRIPE, "Stripe"),
        (PROVIDER_MOLLIE, "Mollie"),
    ]

    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)
    external_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=128)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "external_id"],
                name="unique_webhook_event_per_provider",
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider}:{self.external_id} ({self.event_type})"
