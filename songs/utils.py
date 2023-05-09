import os
import requests
from django.contrib.sites.shortcuts import get_current_site

def check_size(storage, filesize):
    used = storage.used_space
    total = storage.total_space
    actual = upload_calculator(filesize)

    if actual + used < total:
        storage.used_space = actual + used
        return storage
    else:
        return None


def upload_calculator(size):
    return round(size/1000000, 2)


def mb_2_byte(size):
    return size * 1000000


def calculate_size(size):
    x = size
    y = 512000
    if x < y:
        value = round(x/1000, 2)
        ext = ' kb'
    elif x < y*1000:
        value = round(x/1000000, 2)
        ext = ' Mb'
    else:
        value = round(x/1000000000, 2)
        ext = ' Gb'
    return str(value)+ext

def localize_song(song, request=None):
    song_url = song.file.url
    extension = os.path.splitext(song_url)[1]
    local = 'http://localhost:8000'
    secure_domain = lambda domain : f'https://{domain}' if request is not None and request.is_secure else f'http://{domain}'
    current_site = secure_domain(get_current_site(request).domain) if request is not None else local
    song_url = f'{current_site}{song_url}'
    r = requests.get(song_url)
    if r.status_code == 200:
        audio_filename = f'{song.title}{extension}'
        open(audio_filename, 'wb').write(r.content)
        return audio_filename
    return None


