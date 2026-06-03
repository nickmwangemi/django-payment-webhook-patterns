# django-payment-webhook-patterns

A small **portfolio/demo** Django project showing how to handle **Stripe** and **Mollie** payment webhooks with signature verification, idempotent storage, and **pytest** coverage.

This repository is **synthetic** — it does not contain proprietary code, credentials, or business logic from any employer project.

## Highlights

- **Stripe**: verify `Stripe-Signature` via official SDK (`stripe.Webhook.construct_event`)
- **Mollie**: demo HMAC header (`X-Mollie-Signature`) plus form-encoded `id=` payloads (common notification shape)
- **Idempotency**: unique `(provider, external_id)` constraint; duplicates return `200` with `"status": "duplicate"`
- **Tests**: HTTP-level pytest tests with signed synthetic payloads

## Stack

- Python 3.11+
- Django 5
- pytest / pytest-django
- stripe (webhook signature verification only)

## Quick start

```bash
cd django-payment-webhook-patterns
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional — defaults work for local demo

python manage.py migrate
python manage.py runserver
pytest
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health/` | Health check |
| POST | `/webhooks/stripe/` | Stripe signed JSON events |
| POST | `/webhooks/mollie/` | Mollie signed webhooks (form or JSON) |

## Environment variables

| Variable | Default (demo) | Purpose |
|----------|----------------|---------|
| `STRIPE_WEBHOOK_SECRET` | `whsec_synthetic_demo_secret` | Stripe signing secret |
| `MOLLIE_WEBHOOK_SECRET` | `mollie_synthetic_demo_secret` | HMAC secret for demo Mollie handler |
| `DJANGO_SECRET_KEY` | insecure dev default | Django secret |

## Project layout

```
config/           # Django settings & URLs
webhooks/
  handlers/       # Provider-specific verify + parse logic
  services.py     # Idempotent persistence
  views.py        # HTTP endpoints
tests/            # pytest suite
```

## Design notes

**Stripe** — Production apps should always verify webhook signatures before processing events. This repo uses Stripe’s recommended construction helper.

**Mollie** — Live systems often receive a payment `id` and re-fetch status from the Mollie API. This demo adds an HMAC header so you can test authenticity locally without external API calls.

**Idempotency** — Payment webhooks may be retried. Storing a unique provider event id prevents double-settlement bugs.

## Author

**Nicholas Mwangemi** — Backend engineer (Python, Django, payment APIs)

- [LinkedIn](https://www.linkedin.com/in/nick-mwangemi/)
- [GitHub](https://github.com/nickmwangemi)

## License

MIT — see [LICENSE](LICENSE).
