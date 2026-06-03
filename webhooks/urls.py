from django.urls import path

from webhooks.views import HealthView, MollieWebhookView, StripeWebhookView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("webhooks/mollie/", MollieWebhookView.as_view(), name="mollie-webhook"),
]
