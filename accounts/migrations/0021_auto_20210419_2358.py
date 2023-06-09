# Generated by Django 2.2.10 on 2021-04-19 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_auto_20201204_1857'),
    ]

    operations = [
        # migrations.RemoveField(
        #     model_name='artist',
        #     name='whatsapp_phone',
        # ),
        migrations.AddField(
            model_name='artist',
            name='city',
            field=models.CharField(blank=True, max_length=75, null=True, verbose_name='cite'),
        ),
        migrations.AddField(
            model_name='artist',
            name='country',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='Country code'),
        ),
        migrations.AddField(
            model_name='artist',
            name='postal_code',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='Postal Code'),
        ),
        migrations.AddField(
            model_name='artist',
            name='state',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='State code'),
        ),
        migrations.AlterField(
            model_name='artist',
            name='lga',
            field=models.CharField(blank=True, max_length=225, null=True, verbose_name='local government area'),
        ),
    ]
