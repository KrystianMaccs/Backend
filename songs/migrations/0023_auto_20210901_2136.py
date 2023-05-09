# Generated by Django 2.2.10 on 2021-09-01 20:36

from django.db import migrations, models
import django.db.models.deletion
import utils.helper
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0022_songsubscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='cover',
            field=models.ImageField(blank=True, null=True, upload_to=utils.helper.redefinedFileName),
        ),
        migrations.AlterField(
            model_name='song',
            name='cover',
            field=models.ImageField(blank=True, null=True, upload_to=utils.helper.redefinedFileName),
        ),
        migrations.AlterField(
            model_name='song',
            name='file',
            field=models.FileField(upload_to=utils.helper.redefinedSongFileName),
        ),
        migrations.CreateModel(
            name='SongDistributionLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('step', models.CharField(max_length=255)),
                ('message', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='songs.Song')),
            ],
        ),
    ]
