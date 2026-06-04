from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from webhooks.exceptions import (
    DuplicateEventError,
    InvalidPayloadError,
    InvalidSignatureError,
    WebhookError,
)
from webhooks.handlers.mollie import MollieWebhookHandler
from webhooks.handlers.stripe import StripeWebhookHandler
from webhooks.services import persist_webhook_event, process_webhook


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request):
        return _dispatch(
            request,
            handler=StripeWebhookHandler(),
            handle_kwargs={
                "raw_body": request.body,
                "signature_header": request.headers.get("Stripe-Signature"),
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class MollieWebhookView(View):
    def post(self, request):
        return _dispatch(
            request,
            handler=MollieWebhookHandler(),
            handle_kwargs={
                "raw_body": request.body,
                "signature_header": request.headers.get(
                    MollieWebhookHandler.SIGNATURE_HEADER
                ),
                "content_type": request.content_type or "",
            },
        )


def _dispatch(request, handler, handle_kwargs):
    try:
        result = handler.handle(**handle_kwargs)
        stored = persist_webhook_event(result)
        process_webhook(stored)
    except DuplicateEventError:
        return JsonResponse({"status": "duplicate"}, status=200)
    except InvalidSignatureError as exc:
        return JsonResponse({"error": str(exc)}, status=401)
    except InvalidPayloadError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except WebhookError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(
        {
            "status": "ok",
            "provider": result.provider,
            "external_id": result.external_id,
            "event_type": result.event_type,
        },
        status=200,
    )


class HealthView(View):
    def get(self, request):
        return HttpResponse("ok", content_type="text/plain")


class IndexView(View):
    def get(self, request):
        return JsonResponse(
            {
                "health": "/health/",
                "webhooks": {
                    "stripe": "/webhooks/stripe/",
                    "mollie": "/webhooks/mollie/",
                },
            }
        )
