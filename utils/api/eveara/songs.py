from payouts.models import Payout
from songs.tasks import create_distro_log
from .settings import getUserId

from django_q.tasks import async_task
from django.utils import timezone
from datetime import datetime
import random
import os
from songs.models import Song

from .conf import *
from .authentications import authenticated_header
from .distribution import takedown_album


def validate_song(track_file):
    '''
        Validate Song before upload
    '''
    headers = authenticated_header()
    add_song_header = {
        "Authorization": headers['Authorization'],
    }
    files = {'trackFile': track_file}
    r = requests.post(f'{URL}/track/validateTrackFile', files=files,
                      data={}, headers=add_song_header)

    resposne = r.json()
    status = resposne.get('success', False)
    message = resposne.get('message', "")

    return status, message


def upload_eveara_song(track: Song, artist, subscription=None):
    '''
        Upload Song to eveara
    '''

    aim = 'Upload Song to eveara'

    print(aim)
    headers = authenticated_header()
    add_song_header = {
        "Authorization": headers['Authorization'],
    }
    artist_meta = artist.artistmeta
    addable = getUserId() is not None

    r = None
    song_meta = track.songmeta


    if addable:
        genres = track.genres.all()
        availabilities = track.access_availability.all()
        request_data = {}

        lyrics = track.lyrics

        yes_edit = song_meta.disseminate_id is not None

        if not yes_edit:
            request_data["uuid"] = getUserId()
            files = {'trackFile': track.file}
            if song_meta.disseminate_id is None:
                r = requests.post(f'{URL}/track/add', files=files,
                                  data=request_data, headers=add_song_header)

        else:
            request_data = {
                "name": track.title,
                "isrc": track.isrc,
                "iswc": track.iswc,
                "genre": [g.code for g in genres],
                "language": "en",
                "explicit": track.explicit,
                "artists": [int(artist_meta.eveara_artist_id)],
                "availability": [a.code for a in availabilities],
                "albumOnly": track.album_only,
                "lyrics": lyrics if lyrics is not None else ''
            }
            request_data['tracklibraryId'] = song_meta.disseminate_id
            request_data["uuid"] = getUserId()
            r = requests.put(f'{URL}/track/update', data=json.dumps(
                request_data), headers=headers)

        result = None
        message = ''
        if r is not None:
            response = r.json()
            if r.status_code < 300:
                print('Eveara Song Upload ', response)

                if response['success']:
                    if not yes_edit:
                        song_meta.disseminate_id = response['trackId']
                        song_meta.save()

                        message = 'Track upload Successful'

                    if not yes_edit:
                        result = response['trackId']
                result = None
            else:
                print("Eveara API Crashed", response)
                result = None
                message = 'Track upload Failed'

            create_distro_log(track, aim, response.get('message', message))

        if subscription is not None:
            async_task('utils.api.eveara.single_album',
                        song=track, subscription=subscription)

        else:
            print(f'subscription is not present for song {track.title} {track.id}')

        return result

def get_track_albumupload_data(trackId, artist_id):
    return {"trackId": trackId,
            "artists": [int(artist_id)],
            "featuredArtists": [int(artist_id)],
            "participant": [
                {
                    "id": str(PARTICIPANT_ID),
                    "roleId": [1],
                    "payoutSharePercentage":100
                }
            ]}


def single_album(song, subscription):
    '''
        Convert Single track to an album
    '''
    headers = authenticated_header()

    aim = 'Packaging track'
    print('Convert Single track to an album')
    
    song_meta = song.songmeta
    artist = song.artist
    artist_meta = artist.artistmeta
    artist_id = artist_meta.eveara_artist_id

    songs = [get_track_albumupload_data(song_meta.disseminate_id, artist_id)]

    originalReleaseDate = datetime.strftime(song.releaseStartDate, '%d-%m-%Y')

    request_data = {
        "uuid": getUserId(),
        "name": song.title,
        "artists": [artist_id],
        "subscriptionId": subscription.eveara_id,
        "eanupc": song.eanupc,
        "labelId": song.label.disseminate_label_id if song.label is not None else '',
        "originalReleaseDate": originalReleaseDate,
        "coverImage": {
            "url": '',
            "extension": ''
        },
        "tracks": songs
    }

    cover = song.cover
    if cover is not None:
        try:
            album_url = cover.url
            extension = os.path.splitext(cover.file.name)[1].strip('.')
            request_data["coverImage"] = {
                "url": 'https://gocreateafrica.s3.amazonaws.com'+album_url if 'https' not in album_url else album_url,
                "extension": extension
            }
        except Exception as e:
            print("Cover Failed: ", e)

    print(request_data)
    yes_edit = song_meta.eveara_album is not None
    if yes_edit:
        request_data['albumId'] = song_meta.eveara_album

    url_path = '/album/update' if yes_edit else '/album/add'

    if yes_edit:
        r = requests.put(URL+url_path, data=json.dumps(
            request_data), headers=headers)
    else:
        r = requests.post(URL+url_path, data=json.dumps(
            request_data), headers=headers)

    response = r.json()
    print("Singled Albumed ", response)

    message = 'Song Packaging not successful'

    if response['success']:
        message = 'Song successfully packaged'

        if not yes_edit:
            song_meta.eveara_album = response['albumId']
            song_meta.save()

        async_task('utils.api.eveara.distribute_single', song)
    create_distro_log(song, aim, response.get('message', message))




def album_upload(album, subscription=None, is_edit=False):
    headers = authenticated_header()
    artist = album.artist
    album_meta = album.albummeta
    artist_meta = artist.artistmeta
    artist_id = artist_meta.eveara_artist_id

    originalReleaseDate = datetime.strftime(album.releaseStartDate, '%d-%m-%Y')

    songs = album.songs.all()
    track_ids = [upload_eveara_song(
        song, artist, subscription=subscription) if song.disseminate_id is None else song.disseminate_id for song in songs]

    tracks = [get_track_albumupload_data(
        track_id, artist_id) for track_id in track_ids if track_id is not None]

    request_data = {
        "uuid": getUserId(),
        "name": album.title,
        "artists": [artist_id],
        "subscriptionId": subscription.eveara_id,
        "eanupc": album.eanupc,
        "labelId": album.label.disseminate_label_id if album.label is not None else '',
        "originalReleaseDate": originalReleaseDate,
        "coverImage": {
            "url": '',
            "extension": ''
        },
        "tracks": tracks
    }

    yes_edit = album_meta.distribute_id is not None
    if yes_edit:
        request_data['albumId'] = album_meta.distribute_id

    cover = album.cover
    if cover is not None:
        album_url = cover.url
        extension = os.path.splitext(cover.file.name)[1].strip('.')
        request_data["coverImage"] = {
            "url": 'https://gocreateafrica.s3.amazonaws.com'+album_url if 'https' not in album_url else album_url,
            "extension": extension
        }

    url_path = '/album/update' if yes_edit else '/album/add'
    if yes_edit:
        r = requests.put(URL+url_path, data=json.dumps(
            request_data), headers=headers)
    else:
        r = requests.post(URL+url_path, data=json.dumps(
            request_data), headers=headers)

    response = r.json()
    print('Album Response ', response)

    if response['success'] and not is_edit:
        album_meta.distribute_id = response['albumId']
        album_meta.save()


def delete_song(song):
    print('Deleting a on eveara song')
    if song is not None and song.subscription is not None:
        song_meta = song.songmeta
        if song_meta.disseminate_id is not None:
            if song_meta.eveara_album is not None:
                if song.disseminated:
                    takedown_album(song)
                delete_album(song_meta.eveara_album)
            headers = authenticated_header()
            request_data = {"tracklibraryId": str(song_meta.disseminate_id)}

            r = requests.post(f'{URL}/track/delete', data=json.dumps(
                request_data), headers=headers)

            response = r.json()
            print("Delete Track from eveara "+str(response))


def delete_album(eveara_album_id):
    headers = authenticated_header()
    request_data = {"albumId": str(eveara_album_id)}

    r = requests.post(f'{URL}/album/delete', data=json.dumps(
        request_data), headers=headers)

    response = r.json()
    print("Delete Album from eveara "+str(response))


def validate_album(eveara_album_id):
    headers = authenticated_header()

    r = requests.get(f'{URL}/album/validate?albumId=' + str(eveara_album_id), headers=headers)
    print(eveara_album_id)

    response = r.json()
    return response

def song_report(song, songsale):
    headers = authenticated_header()
    song_meta = song.songmeta

    today = timezone.now()

    # request_data = {
    #     "uuid": getUserId(),
    #     "month": str(today.month),
    #     "year": str(today.year),
    #     "limit": "1",
    #     "offset": "0",
    #     "searchTerm": "",
    #     "albumId": "",
    #     "trackId": str(song_meta.disseminate_id)
    # }

    query_param = f'uuid={getUserId()}&month={str(today.month)}&year={str(today.year)}&limit=1&offset=0&searchTerm=&albumId=&trackId={str(song_meta.disseminate_id)}'

    r = requests.get(f'{URL}/reports/salesByTracks?'+query_param, headers=headers)

    response = r.json()
    if r.status_code < 300:
        if response['success']:
            if len(response['data']) > 0:
                data = response['data'][0]
                if str(song.disseminate_id) == data.get("trackId", ""):
                    payout = Payout.objects.get(
                        pay_due__id=songsale.pay_due__id)
                    songsale.revenue = float(data.get('amount', 0))
                    songsale.played_count = int(data.get('playCount', 0))
                    song.isrc = data.get('isrc', "")
                    song.iswc = data.get('iswc', "")
                    songsale.save()
                    song.save()

                    payout.amount = float(data.get('amount', 0))
                    payout.song_tracked_count += 1
                    payout.save()
            print('Song Report Response ', response)
        else:
            print("Song Report Error from Eveara API", response)
    else:
        print("Song Report Eveara API Crashed", response)


def test_song_report(song, songsale):
    payout = Payout.objects.get(
        pay_due__id=songsale.pay_due_id)
    played_count = random.randrange(1, 1000000)
    amount = played_count * 2.5

    songsale.revenue = amount
    songsale.played_count = played_count

    if payout.amount is None:
        payout.amount = 0

    payout.amount = amount
    payout.song_tracked_count += 1

    songsale.save()
    # song.save()
    payout.save()
