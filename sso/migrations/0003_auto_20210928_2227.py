# Generated by Django 2.2.10 on 2021-09-28 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sso', '0002_auto_20210925_0200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appauthlog',
            name='accessToken',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='appauthlog',
            name='app_user_agent',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='appauthlog',
            name='client_user_agent',
            field=models.CharField(max_length=255),
        ),
    ]
