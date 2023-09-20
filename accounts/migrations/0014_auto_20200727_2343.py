# Generated by Django 2.2.10 on 2020-07-27 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_artistmeta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='nationality',
        ),
        migrations.AddField(
            model_name='artist',
            name='gender',
            field=models.CharField(blank=True, default='O', max_length=1,
                                   null=True, verbose_name='M Male, F Female, O thers'),
        ),
        migrations.AddField(
            model_name='artist',
            name='zipcode',
            field=models.CharField(
                blank=True, max_length=8, null=True, verbose_name='Address Zipcode'),
        ),
        migrations.AddField(
            model_name='artistmeta',
            name='eveara_user_id',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]