# Generated by Django 4.2.3 on 2023-09-20 20:52

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArtistSubscription",
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
                ("songs_added", models.IntegerField(default=0)),
                ("expired", models.BooleanField(default=False)),
                ("activated", models.BooleanField(default=False)),
                ("provisioned", models.BooleanField(default=False)),
                ("eveara_id", models.IntegerField(default=0, null=True)),
                ("last_renewed", models.DateTimeField(blank=True, null=True)),
                ("expired_timestamp", models.DateTimeField(blank=True, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "artist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.artist",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Package",
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
                ("title", models.CharField(max_length=35)),
                ("description", models.CharField(max_length=225)),
                ("tracks_count", models.IntegerField(default=0)),
                ("eta_months", models.IntegerField(default=0)),
                ("eta_years", models.IntegerField(default=0)),
                ("sku_id", models.CharField(blank=True, max_length=15, null=True)),
                ("eveara_id", models.IntegerField(default=0, null=True)),
                (
                    "feature",
                    models.CharField(
                        choices=[
                            ("GO_DISTRO", "Go Distro"),
                            ("GO_MONITOR", "Go Monitor"),
                        ],
                        default="GO_DISTRO",
                        max_length=50,
                    ),
                ),
                ("price", models.FloatField()),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="SubscriptionTransaction",
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
                ("is_successful", models.BooleanField(default=False)),
                ("payment_gateway", models.CharField(default="STRIPE", max_length=30)),
                (
                    "transaction_reference",
                    models.CharField(max_length=150, unique=True),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "subscription",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="subscriptions.artistsubscription",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="artistsubscription",
            name="package",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="subscriptions.package"
            ),
        ),
    ]
