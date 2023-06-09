# Generated by Django 2.2.10 on 2020-08-31 02:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SystemDefault',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=45)),
                ('description', models.CharField(max_length=75)),
                ('nkey', models.CharField(max_length=45)),
                ('nvalue', models.CharField(max_length=75)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
