# Generated by Django 2.2.10 on 2021-01-29 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systemcontrol', '0002_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='eveara_user_id',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
    ]
