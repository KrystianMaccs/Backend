# Generated by Django 2.2.10 on 2021-02-04 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_auto_20201112_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='sku_id',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
