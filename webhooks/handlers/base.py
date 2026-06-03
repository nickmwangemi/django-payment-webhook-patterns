from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WebhookResult:
    """Outcome of handling a single provider webhook."""

    provider: str
    external_id: str
    event_type: str
    payload: dict[str, Any]
    duplicate: bool = False
