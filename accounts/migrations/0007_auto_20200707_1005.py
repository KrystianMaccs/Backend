# Generated by Django 3.0.6 on 2020-07-07 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20200707_1001'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffprofile',
            name='image',
        ),
        migrations.AlterField(
            model_name='userphoto',
            name='image',
            field=models.ImageField(null=True, upload_to='files/profile-pictures'),
        ),
    ]