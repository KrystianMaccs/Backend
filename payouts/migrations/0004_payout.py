# Generated by Django 4.2.3 on 2023-08-22 11:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payouts", "0003_delete_payout"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payout",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("payment_approved", models.BooleanField(default=False)),
                ("amount", models.FloatField(blank=True, null=True)),
                ("approval_timestamp", models.DateTimeField(null=True)),
                ("song_tracked_count", models.IntegerField(default=0)),
                ("triggered", models.BooleanField(default=False)),
                ("last_triggered", models.DateTimeField(null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "confirm_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "pay_due",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="payouts.payoutdue",
                    ),
                ),
            ],
        ),
    ]
