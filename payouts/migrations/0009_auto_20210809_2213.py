# Generated by Django 2.2.10 on 2021-08-09 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payouts', '0008_auto_20201227_2218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='songsales',
            name='revenue',
            field=models.FloatField(default=0),
        ),
    ]
