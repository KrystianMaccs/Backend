# Generated by Django 2.2.10 on 2020-07-18 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20200713_0114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name='nationality',
            field=models.CharField(blank=True, max_length=35, null=True, verbose_name='Nationality'),
        ),
        migrations.AlterField(
            model_name='artist',
            name='whatsapp_phone',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='whatsapp'),
        ),
    ]
