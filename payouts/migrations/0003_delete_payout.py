# Generated by Django 4.2.3 on 2023-08-22 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payouts", "0002_payout_pay_due"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Payout",
        ),
    ]