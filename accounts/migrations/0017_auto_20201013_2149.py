# Generated by Django 2.2.10 on 2020-10-13 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_bankaccount_recipient_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artiststorage',
            name='total_space',
            field=models.FloatField(default=200),
        ),
    ]