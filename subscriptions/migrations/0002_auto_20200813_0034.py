# Generated by Django 2.2.10 on 2020-08-13 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artistsubscription',
            name='cancel_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='artistsubscription',
            name='last_renewed',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
