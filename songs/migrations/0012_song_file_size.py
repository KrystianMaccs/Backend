# Generated by Django 2.2.10 on 2020-10-04 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0011_auto_20200914_1957'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='file_size',
            field=models.IntegerField(default=0),
        ),
    ]
