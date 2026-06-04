# django-payment-webhook-patterns

Django demo: Stripe and Mollie webhook handlers with signature verification, idempotent event storage, pytest.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
pytest
```

## Endpoints

| Method | Path |
|--------|------|
| GET | `/health/` |
| POST | `/webhooks/stripe/` |
| POST | `/webhooks/mollie/` |

Env: `STRIPE_WEBHOOK_SECRET`, `MOLLIE_WEBHOOK_SECRET` (see `.env.example`). Defaults work for local demo.

MIT
