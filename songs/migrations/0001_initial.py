# Generated by Django 4.2.3 on 2023-08-22 10:39

from django.db import migrations, models
import django.db.models.deletion
import utils.helper
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("royalty", "0003_auto_20200831_1818"),
        ("subscriptions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessAvailability",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=50)),
                ("code", models.IntegerField()),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Album",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=55)),
                ("description", models.CharField(max_length=100)),
                (
                    "cover",
                    models.ImageField(
                        blank=True, null=True, upload_to=utils.helper.redefinedFileName
                    ),
                ),
                ("preSalesDate", models.DateField(null=True)),
                ("originalReleaseDate", models.DateField(null=True)),
                ("releaseEndDate", models.DateField(null=True)),
                ("eanupc", models.CharField(blank=True, max_length=15, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "artist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.artist",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=50)),
                ("code", models.IntegerField()),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Label",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=45)),
                (
                    "description",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "disseminate_label_id",
                    models.CharField(blank=True, max_length=11, null=True),
                ),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "artist",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.artist",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Song",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=55)),
                ("description", models.CharField(max_length=100)),
                (
                    "file",
                    models.FileField(upload_to=utils.helper.redefinedSongFileName),
                ),
                ("file_size", models.IntegerField(default=0)),
                (
                    "encoded",
                    models.FileField(
                        blank=True, null=True, upload_to="files/artist/songs/encoded"
                    ),
                ),
                (
                    "cover",
                    models.ImageField(
                        blank=True, null=True, upload_to=utils.helper.redefinedFileName
                    ),
                ),
                ("duration_in_ms", models.IntegerField(default=0)),
                ("isrc", models.CharField(blank=True, max_length=17, null=True)),
                ("iswc", models.CharField(blank=True, max_length=17, null=True)),
                ("publisher", models.CharField(blank=True, max_length=35, null=True)),
                ("version", models.CharField(blank=True, max_length=35, null=True)),
                ("writer", models.CharField(blank=True, max_length=35, null=True)),
                ("composer", models.CharField(blank=True, max_length=35, null=True)),
                ("arranger", models.CharField(blank=True, max_length=35, null=True)),
                ("upc", models.CharField(blank=True, max_length=17, null=True)),
                ("explicit", models.BooleanField(default=True)),
                ("album_only", models.BooleanField(default=False)),
                ("disseminated", models.BooleanField(default=False)),
                ("lyrics", models.TextField(blank=True, null=True)),
                ("eanupc", models.CharField(blank=True, max_length=15, null=True)),
                ("preSalesDate", models.DateField(null=True)),
                ("releaseEndDate", models.DateField(null=True)),
                ("releaseStartDate", models.DateField(null=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "access_availability",
                    models.ManyToManyField(blank=True, to="songs.accessavailability"),
                ),
                (
                    "artist",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.artist",
                    ),
                ),
                ("genres", models.ManyToManyField(blank=True, to="songs.genre")),
                (
                    "label",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="songs.label",
                    ),
                ),
                (
                    "subscription",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="subscriptions.artistsubscription",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SongSubscription",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "song",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="songs.song"
                    ),
                ),
                (
                    "subscription",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="subscriptions.artistsubscription",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SongMeta",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "disseminate_id",
                    models.CharField(blank=True, max_length=10, null=True),
                ),
                (
                    "eveara_album",
                    models.CharField(blank=True, max_length=15, null=True),
                ),
                (
                    "djm_fingerprint_id",
                    models.CharField(blank=True, max_length=35, null=True),
                ),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "song",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="songs.song"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SongLink",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("storeName", models.CharField(max_length=150)),
                ("link", models.URLField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "song",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="songs.song"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SongDistributionLog",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("step", models.CharField(max_length=255)),
                ("message", models.CharField(max_length=255)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "song",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="songs.song"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RoyaltySplit",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=15)),
                ("fullname", models.CharField(max_length=105)),
                ("share", models.FloatField()),
                ("paid", models.BooleanField(default=False)),
                ("total_paid", models.FloatField(null=True)),
                (
                    "description",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("is_verified", models.BooleanField(default=False)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "royalty",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="royalty.royalty",
                    ),
                ),
                (
                    "song",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="songs.song"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RadioPlay",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("radio_name", models.CharField(max_length=150)),
                ("radio_id", models.CharField(max_length=150)),
                ("query_date", models.DateField()),
                ("duration", models.DurationField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "song",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="songs.song"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AlbumMeta",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "distribute_id",
                    models.CharField(blank=True, max_length=11, null=True),
                ),
                ("disseminated", models.BooleanField(default=False)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "album",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="songs.album"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="album",
            name="label",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="songs.label",
            ),
        ),
        migrations.AddField(
            model_name="album",
            name="songs",
            field=models.ManyToManyField(blank=True, to="songs.song"),
        ),
        migrations.AddField(
            model_name="album",
            name="subscription",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="subscriptions.artistsubscription",
            ),
        ),
    ]
