# Generated by Django 2.2.10 on 2020-12-27 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payouts', '0006_auto_20201227_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artistpayout',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=25, null=True, unique=True),
        ),
    ]
