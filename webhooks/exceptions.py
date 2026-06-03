class WebhookError(Exception):
    """Base webhook processing error."""


class InvalidSignatureError(WebhookError):
    """Raised when provider signature verification fails."""


class InvalidPayloadError(WebhookError):
    """Raised when the webhook body cannot be parsed or is invalid."""


class DuplicateEventError(WebhookError):
    """Raised when the same provider event was already processed."""
