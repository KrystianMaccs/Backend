# Generated by Django 2.2.10 on 2021-05-29 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0007_auto_20210519_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistsubscription',
            name='provisioned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscriptiontransaction',
            name='is_successful',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscriptiontransaction',
            name='payment_gateway',
            field=models.CharField(default='STRIPE', max_length=30),
        ),
    ]