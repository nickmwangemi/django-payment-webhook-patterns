# django-payment-webhook-patterns

Demo Django project: Stripe and Mollie webhook signature verification, idempotent event storage, pytest coverage.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
pytest
```

Copy `.env.example` to `.env` if you want to override defaults.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health/` | Health check |
| POST | `/webhooks/stripe/` | Stripe signed JSON events |
| POST | `/webhooks/mollie/` | Mollie signed webhooks (form or JSON) |

## Environment

| Variable | Default |
|----------|---------|
| `STRIPE_WEBHOOK_SECRET` | `whsec_synthetic_demo_secret` |
| `MOLLIE_WEBHOOK_SECRET` | `mollie_synthetic_demo_secret` |
| `DJANGO_SECRET_KEY` | insecure dev default |

## Layout

```
config/           # settings & URLs
webhooks/handlers # verify + parse per provider
webhooks/services # idempotent persistence
tests/
```

**Nicholas Mwangemi** — [LinkedIn](https://www.linkedin.com/in/nick-mwangemi/) · [GitHub](https://github.com/nickmwangemi)

MIT — see [LICENSE](LICENSE).
