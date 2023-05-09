from .conf import *
from .songs import *
from .outlets import *
from .accounts import *
from .distribution import *
from .subscriptions import *
from .authentications import authenticated_header

from songs.models import Genre, AccessAvailability


def create_participant(isni=None, ipn=None, is_edit=False):
    global PARTICIPANT_ID

    headers = authenticated_header()
    request_data = {
        "uuid": getUserId(),
        "name": "GoCreate",
        "isni": isni if isni is not None else '',
        "ipn": ipn if ipn is not None else ''
    }

    if is_edit:
        request_data['participantId'] = PARTICIPANT_ID
        r = requests.put(f'{URL}/participant/update ', data=json.dumps(
            request_data), headers=headers)

    else:
        r = requests.post(f'{URL}/participant/add ', data=json.dumps(
            request_data), headers=headers)

    response = r.json()
    if r.status_code < 300:
        if response['success']:
            PARTICIPANT_ID = response['participantId']
            print("PARTICIPANT ID: ", PARTICIPANT_ID)


def publish_genres():
    headers = authenticated_header()
    r = requests.get(f'{URL}/genres/get', headers=headers)
    if r.status_code == 200:
        response = r.json()
        results = response['data']
        genres = []
        for g in results:
            try:
                genre = Genre.objects.get(title=g.get('name', ''))
                genre.code = g.get('genreId', 0)
                genre.save()
            except:
                genre = Genre()
                genre.title = g.get('name', '')
                genre.code = g.get('genreId', 0)
                genres.append(genre)
        Genre.objects.bulk_create(genres)


def publish_access_avail():
    headers = authenticated_header()
    r = requests.get(f'{URL}/availabilities/get', headers=headers)
    if r.status_code == 200:
        response = r.json()
        results = response['data']
        avails = []
        for a in results:
            try:
                avail = AccessAvailability.objects.get(title=a.get('name', ''))
                avail.code = a.get('availabilityId', 0)
                avail.save()
            except:
                avail = AccessAvailability()
                avail.title = a.get('name', '')
                avail.code = a.get('availabilityId', 0)
                avails.append(avail)
        AccessAvailability.objects.bulk_create(avails)
