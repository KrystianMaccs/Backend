from accounts.models import Artist
from .conf import *
from datetime import datetime
from systemcontrol.models import Settings

from .settings import getUserId
from .authentications import authenticated_header

from django_q.tasks import async_task



def create_artist(artist: Artist, is_new_prod: bool = False):
    headers = authenticated_header()
    artist_meta = artist.artistmeta
    is_edit = artist_meta.eveara_user_id is not None

    request_data = {
        "uuid": getUserId(),
        "artistname": artist.stage_name.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}),
        "country": artist.country if artist.country is not None else "NG"
    }

    if is_edit and not is_new_prod:
        request_data["artistid"] = artist_meta.eveara_artist_id
        r = requests.put(f'{URL}/artist/update', data=json.dumps(
            request_data), headers=headers)
    else:
        request_data = {
            "uuid": getUserId(),
            "name": artist.stage_name.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}),
            "country": "NG"
        }
        r = requests.post(f'{URL}/artist/add', data=json.dumps(
            request_data), headers=headers)

    response = r.json()

    print("Add New Artist ", response)

    if response['success'] and not is_edit:
        artist_meta.eveara_artist_id = response['artistId']
        artist_meta.save()
    elif response.get('message', '') == 'Artist name already exists' and not is_edit:
        search_artist(artist)


def label(label, is_edit=False, is_new_prod=False):
    headers = authenticated_header()

    if not is_edit and label.disseminate_label_id is not None:
        return None

    addable = getUserId() is not None

    if addable:
        request_data = {
            "name": label.title.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"})
        }

        if is_edit and not is_new_prod:
            request_data = {
                "labelName": label.title.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}),
                'labelId': label.disseminate_label_id
            }
            r = requests.put(f'{URL}/label/update', data=json.dumps(
                request_data), headers=headers)
        else:
            request_data['uuid'] = getUserId()
            r = requests.post(f'{URL}/label/add', data=json.dumps(
                request_data), headers=headers)

        response = r.json()
        print('Label Response ', response)

        if response['success'] and not is_edit:
            label.disseminate_label_id = response['labelId']
            label.save()

        elif 'exists' in response['message'].lower():
            async_task("utils.api.eveara.search_label", label)


def delete_label(label_id):
    headers = authenticated_header()
    request_data = {
        "labelId": label_id
    }
    r = requests.post(f'{URL}/label/delete', data=json.dumps(
        request_data), headers=headers)

    response = r.json()
    print('Delete Label ', response)


def search_label(label):
    headers = authenticated_header()
    r = requests.get(
        f'{URL}/label/get?uuid={getUserId()}&searchTerm={label.title}&limit=1&offset=0', headers=headers)

    response = r.json()
    print('Search Label ', response)

    totalRecords = response.get('totalRecords', 0)
    if totalRecords > 0:
        data = response.get('data')
        result = data[0]
        label.disseminate_label_id = result.get('labelId')
        label.save()


def search_artist(artist):
    print("Searching Artist")
    headers = authenticated_header()

    artist_stage_name = artist.stage_name
    artist_meta = artist.artistmeta
    request_data = {
        "uuid": getUserId(),
        "searchTerm": artist_stage_name,
        "artistId": "",
                    "limit": "10",
                    "offset": "0"
    }

    r = requests.post(f'{URL}/artist/get', data=json.dumps(
        request_data), headers=headers)

    response = r.json()
    if r.status_code < 300:
        if response['success']:
            if response['totalRecords'] > 0:
                data = response['data']

                for d in data:
                    if d['name'] == artist_stage_name:
                        print("Found Artist ", d)
                        artist_meta.eveara_artist_id = d['artistId']
                        artist_meta.save()
                        break


def get_countries():
    global outlets
    headers = authenticated_header()

    r = requests.get(f'{URL}/countries/get', headers=headers)

    response = r.json()
    return response
