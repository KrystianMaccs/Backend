# Generated by Django 2.2.10 on 2020-08-13 00:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_auto_20200727_2343'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='artist',
            name='zipcode',
        ),
    ]
