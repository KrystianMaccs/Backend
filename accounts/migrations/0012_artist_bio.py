# Generated by Django 2.2.10 on 2020-07-23 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20200718_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='bio',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
    ]
