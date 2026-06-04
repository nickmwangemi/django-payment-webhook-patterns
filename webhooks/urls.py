from django.urls import path

from webhooks.views import HealthView, IndexView, MollieWebhookView, StripeWebhookView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("health/", HealthView.as_view(), name="health"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("webhooks/mollie/", MollieWebhookView.as_view(), name="mollie-webhook"),
]
