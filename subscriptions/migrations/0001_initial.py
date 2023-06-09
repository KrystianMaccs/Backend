# Generated by Django 2.2.10 on 2020-08-13 00:30

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0015_auto_20200813_0030'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistSubscription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('songs_added', models.IntegerField(default=0)),
                ('cancel', models.BooleanField(default=False)),
                ('last_renewed', models.DateTimeField()),
                ('cancel_timestamp', models.DateTimeField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Artist')),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=35)),
                ('description', models.CharField(max_length=225)),
                ('tracks_count', models.IntegerField(default=0)),
                ('eta_months', models.IntegerField(default=0)),
                ('eta_years', models.IntegerField(default=0)),
                ('price', models.FloatField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_reference', models.CharField(max_length=35, unique=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscriptions.ArtistSubscription')),
            ],
        ),
        migrations.AddField(
            model_name='artistsubscription',
            name='package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscriptions.Package'),
        ),
    ]
