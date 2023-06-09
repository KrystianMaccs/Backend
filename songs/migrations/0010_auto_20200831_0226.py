# Generated by Django 2.2.10 on 2020-08-31 02:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0009_song_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='preSalesDate',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='releaseEndDate',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='royaltysplit',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='royaltysplit',
            name='total_paid',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='song',
            name='eanupc',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='song',
            name='label',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='songs.Label'),
        ),
        migrations.AddField(
            model_name='song',
            name='preSalesDate',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='song',
            name='releaseEndDate',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='song',
            name='releaseStartDate',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='songmeta',
            name='eveara_album',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
