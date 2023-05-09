from django.core.cache import cache

DEFAULT_TIMEOUT = 60 * 60


def set_song_update_in_progress_status(song_update_in_progress):
    return cache.set('song_update_in_progress', song_update_in_progress, DEFAULT_TIMEOUT)


def get_song_update_in_progress_status():
    return cache.get_or_set('song_update_in_progress', False, DEFAULT_TIMEOUT)
