# Generated by Django 2.2.10 on 2020-07-23 01:21

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('royalty', '0001_initial'),
        ('accounts', '0012_artist_bio'),
        ('songs', '0002_auto_20200707_0931'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='artist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Artist'),
        ),
        migrations.CreateModel(
            name='RoyaltySplit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=15)),
                ('fullname', models.CharField(max_length=105)),
                ('share', models.FloatField()),
                ('description', models.CharField(max_length=100)),
                ('is_verified', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('royalty', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='royalty.Royalty')),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='songs.Song')),
            ],
        ),
    ]
