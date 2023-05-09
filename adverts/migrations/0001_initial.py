# Generated by Django 2.2.10 on 2020-10-07 16:38

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=45)),
                ('description', models.CharField(max_length=255)),
                ('expiry_month', models.IntegerField(default=1)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Advert',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('details', models.TextField(blank=True)),
                ('file_type', models.CharField(max_length=15)),
                ('file', models.FileField(upload_to='files/adverts')),
                ('visits', models.IntegerField(default=0)),
                ('short_text', models.CharField(blank=True, max_length=155, null=True)),
                ('link', models.URLField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adverts.Plan')),
            ],
        ),
    ]
