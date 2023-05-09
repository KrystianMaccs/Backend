from songs.tasks import create_distro_log
from .conf import *
from .outlets import get_outlets
from .settings import getUserId
from .authentications import authenticated_header

from datetime import datetime


def distribute_single(song):
    global outlets
    print('Distributing Singles Eveara')

    aim = 'Publishing track'

    headers = authenticated_header()
    outlets = outlets if len(outlets) > 0 else get_outlets()

    song_meta = song.songmeta
    preSalesDate = datetime.strftime(song.preSalesDate, '%d-%m-%Y')
    releaseStartDate = datetime.strftime(song.releaseStartDate, '%d-%m-%Y')
    releaseEndDate = datetime.strftime(song.releaseEndDate, '%d-%m-%Y')

    outletsDetails = [{
        "storeId": int(outletId),
        "preSalesDate": preSalesDate,
        "releaseStartDate": releaseStartDate,
        "releaseEndDate": releaseEndDate
    } for outletId in outlets]

    request_data = {
        "uuid": getUserId(),
        "albumId": int(song_meta.eveara_album),
        "outletsDetails": outletsDetails
    }

    r = requests.post(f'{URL}/outlets/distribute', data=json.dumps(
        request_data), headers=headers)

    response = r.json()

    message = 'Track publishing failed'

    if r.status_code < 300:
        if response['success']:
            song.disseminated = True
            song.save()

            message = 'Track Publish Successful'
            print("Single Track Distributed ", response)

        else:
            print("Error from Eveara API distributed", response)
    else:
        print("Eveara API Crashed distribution", response)

    
    create_distro_log(song, aim, response.get('message', message))


def distribute_album(album):
    headers = authenticated_header()
    outlets = get_outlets()

    album_meta = album.albummeta
    preSalesDate = str(album.preSalesDate)
    releaseStartDate = str(album.originalReleaseDate)
    releaseEndDate = str(album.releaseEndDate)

    outletsDetails = [{
        "storeId": int(outletId),
        "preSalesDate": preSalesDate,
        "releaseStartDate": releaseStartDate,
        "releaseEndDate": releaseEndDate
    } for outletId in outlets]

    request_data = {
        "uuid": getUserId(),
        "albumId": int(album_meta.distribute_id),
        "outletsDetails": outletsDetails
    }

    r = requests.post(f'{URL}/royaltyPayment/payouts', data=json.dumps(
        request_data), headers=headers)

    response = r.json()
    if r.status_code < 300:
        if response['success']:
            album_meta.disseminated = True
            album_meta.save()
            print("Album Distributed")
        else:
            print("Error from Eveara API", response)
    else:
        print("Eveara API Crashed", response)



def redistribute(song):
    print('Redistributing Song on eveara')
    song_meta = song.songmeta
    eveara_album_id = song_meta.eveara_album
    outlets = get_album_outlets(eveara_album_id)
    outlets = [int(o['storeId']) for (o) in outlets]

    headers = authenticated_header()
    request_data = {
        'uuid': getUserId(),
        'albumId': eveara_album_id,
        "stores": outlets
    }

    r = requests.put(f'{URL}/outlets/update', data=json.dumps(
        request_data), headers=headers)

    response = r.json()

    if response['success']:
        print("Redistributed Song ", response)
        song.disseminated = True
        song.save()
    else:
        print(f"Eveara Album Redistribution: {response['message']}")


def takedown_album(song):
    song_meta = song.songmeta
    eveara_album_id = song_meta.eveara_album
    outlets = get_album_outlets(eveara_album_id)
    outlets = [int(o['storeId']) for (o) in outlets]

    headers = authenticated_header()
    request_data = {
        'uuid': getUserId(),
        'albumId': eveara_album_id,
        "stores": outlets
    }

    r = requests.put(f'{URL}/outlets/takedown', data=json.dumps(
        request_data), headers=headers)

    response = r.json()

    if not response['success']:
        print(f"Eveara Album Takedown: {response['message']}")
    print("Take down Song ", response)
    song.disseminated = False
    song.save()


def get_album_outlets(eveara_album_id):

    headers = authenticated_header()
    request_data = {
        'albumId': eveara_album_id
    }

    r = requests.post(f'{URL}/outlets/getDetailsByAlbum', data=json.dumps(
        request_data), headers=headers)

    response = r.json()

    if not response['success']:
        raise ValueError(f"Eveara: {response['message']}")

    data = response['data']
    return data
