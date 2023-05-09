from random import randint, randrange, choices
from datetime import datetime
from django_q.tasks import async_task
from django.core.cache import cache
from django.utils import timezone

from utils.helper import date2string

from .DJMonitorAPI import DJMFingerprintBucket, DJMRadioStreams
from utils.song import localize_song

import json

DEFAULT_TIMEOUT = 60 * 60 * 2

project_key = "4353e976fb192c18c02c654dbf826a2c"
project_secret = "99c636de4d4535615951b04d16197d37"

console_api_key = '4473e588b35568687564de38ed134d0b'
console_api_secret = '5fb92e20138ce20695dbb6e7887ce8de'

djmRadioApi: DJMRadioStreams = DJMRadioStreams(project_key, project_secret)
djmFingerprintBucketApi: DJMFingerprintBucket = DJMFingerprintBucket(
    console_api_key, console_api_secret, "GoCreate")


def create_track_fingerprint(track, request=None):
    file_name = localize_song(track, request)
    song_meta = track.songmeta
    metadata = {
        "custom_tag": song_meta.disseminate_id,
        "title": track.title,
        "artist": track.artist.stage_name.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}),
        "version": track.version if track.version is not None else '',
        "label": track.label.title if track.label is not None else '',
        "isrc": track.isrc if track.isrc is not None else '',
        "iswc": track.iswc if track.iswc is not None else '',
        "publisher": track.publisher if track.publisher is not None else '',
        "writer": track.writer if track.writer is not None else '',
        "composer": track.composer if track.composer is not None else '',
        "arranger": track.arranger if track.arranger is not None else '',
        "upc": track.upc if track.upc is not None else ''
    }
    result = djmFingerprintBucketApi.add_fingerprint(file_name, metadata)
    result = json.loads(result)
    async_task('os.remove', file_name)
    song_meta.djm_fingerprint_id = result.get('djm_fingerprint_id', None)
    track.duration_in_ms = result.get('duration_in_ms', 0)
    song_meta.save()
    track.save()

    print('Finger printed added ', song_meta.djm_fingerprint_id)


def delete_track_fingerprint(track):
    song_meta = track.songmeta

    result = djmFingerprintBucketApi.remove_fingerprint(
        {'djm_fingerprint_id': song_meta.djm_fingerprint_id})
    result = json.loads(result)

    try:
        song_meta.djm_fingerprint_id = None
        track.duration_in_ms = 0

        song_meta.save()
        track.save()
    except:
        pass

    print("Status ", result.get('status', 'No message'))


def getStreamStatus():
    result = djmRadioApi.get_status_of_radio_streams()
    result = json.loads(result)
    return result


def getRadioPlaylist(valiated_data):
    now = timezone.now()
    radio_id = valiated_data.get('radio_stream_id', None)
    date = valiated_data.get('date', str(now.date()))
    result = djmRadioApi.fetch_radio_stream_playlist_for_date(
        {'radio_stream_id': radio_id, "date": date})
    result = json.loads(result)

    return result


def getFingerPlayed(fingerprint_id: str, year: int, month: int):
    """
    returns { 
        "code":0,
        "djm_fingerprint_id":"Dc1c31060822713201e3418b3e979ff9a",
        "plays":
        [
            {
                "start_time":"2021-03-09 15:08:18.769443",
                "end_time":"2021-03-09 15:08:18.769443",
                "radio_stream":
                {
                    "radio_stream_id":"RSc65570a87731da64f967371e8017f250",
                    "name":"Cool FM 96.9 Lagos"
                }
            }
        ]
    }
    """
    now = timezone.now()

    date = f'{year}-{month}'

    key: str = 'djm_fingerprint_id_'+fingerprint_id
    result = cache.get(key)
    if result is None:
        result = djmFingerprintBucketApi.get_fingerprint_plays(
            {'djm_fingerprint_id': fingerprint_id, "month": date})
        cache.set(key, result, DEFAULT_TIMEOUT)

    result = json.loads(result)

    if result.get('code', 1) == 0:
        result = result.get('plays')
    else:
        result = None

    return result


def get_random_datetime(year: int, month: int):
    rand_hour = randrange(1, 24)
    rand_min = randrange(1, 30)
    end_min = rand_min + randrange(1, 30)

    start = datetime(year, month, 1, rand_hour, rand_min)
    end = datetime(year, month, 1, rand_hour, end_min)

    return date2string(start), date2string(end)


radio_name = ['Cool Fm', 'Lagos Fm', 'Thrillee FM',
              'Stiles FM', 'Iyiola FM', 'Gocreate FM']


def generate_play_data(year: int, month: int):
    start, end = get_random_datetime(year, month)
    rand_fm = choices(radio_name)[0]

    return {
        'start_time': start,
        'end_time': end,
        "radio_stream":
        {
            "radio_stream_id": rand_fm,
            "name": rand_fm
        }
    }


def getTestFingerPlayed(fingerprint_id: str, year: int, month: int):
    play_counts = randint(1, 25)

    return list((generate_play_data(year, month) for _ in range(play_counts)))
