from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WebhookEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        choices=[("stripe", "Stripe"), ("mollie", "Mollie")],
                        max_length=32,
                    ),
                ),
                ("external_id", models.CharField(max_length=255)),
                ("event_type", models.CharField(max_length=128)),
                ("payload", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="webhookevent",
            constraint=models.UniqueConstraint(
                fields=("provider", "external_id"),
                name="unique_webhook_event_per_provider",
            ),
        ),
    ]
