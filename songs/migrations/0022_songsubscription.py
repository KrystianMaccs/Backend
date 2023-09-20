# Generated by Django 2.2.10 on 2021-06-19 19:02

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0009_package_feature'),
        ('songs', '0021_auto_20210526_1957'),
    ]

    operations = [
        migrations.CreateModel(
            name='SongSubscription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='songs.Song')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscriptions.ArtistSubscription')),
            ],
        ),
    ]