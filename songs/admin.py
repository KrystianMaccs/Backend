from django.contrib import admin

from .models import Song, Album, Label, Genre, AccessAvailability, SongDistributionLog


admin.site.register(Genre)
admin.site.register(Label)
admin.site.register(AccessAvailability)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'timestamp'
    )

    search_fields = (
        'title',
    )


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = (
        'artist',
        'title',
        'timestamp'
    )

    list_filter = (
        'artist',
        'timestamp'
    )


@admin.register(SongDistributionLog)
class DistroLogAdmin(admin.ModelAdmin):
    list_display = (
        'song',
        'step',
        'message',
        'timestamp'
    )

    list_filter = (
        'step',
        'timestamp'
    )

    search_fields = (
        'song__title',
        'song__artist__stage_name',
        'step',
        'message'
    )
