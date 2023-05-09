from systemcontrol.models import Settings

from .authentications import authenticated_header
from .conf import (
    URL,
)

import requests
import json


# getUserId() = 'B93240B3-CDF6-1CE8-7442FA178F52386A'
def getUserId():
    defaults = Settings.objects.first()
    if defaults is None:
        defaults = create_user()

    return defaults.eveara_user_id


def create_user(artist=None, is_edit=False):
    headers = authenticated_header()
    request_data = {
        "firstName": 'Gocreate',
        "surName": "Eveara",
        "email": 'gocreateapp@gmail.com',
        "gender": "M",
        "address": {
            "house": 'Gocreate',
            "street": 'Gocreate',
            "city": 'Gocreate',
            "zip": '000000',
            "mobile": '08063998195'
        },
        "country": "NG",
        "state": "LA",
        "language": "en"
    }

    if is_edit:
        dob = "11-06-2020"
        request_data['ismailsubscribed'] = "0"
        request_data['dateofbirth'] = dob

        r = requests.put(f'{URL}/user/update', data=json.dumps(
            request_data), headers=headers)
    else:
        r = requests.post(f'{URL}/user/add', data=json.dumps(
            request_data), headers=headers)

    response = r.json()
    print('Create new Response ', response)

    if response['success'] and not is_edit:
        settings = Settings.objects.first()
        if settings is None:
            settings = Settings.objects.create(eveara_user_id=response["uuid"])
        else:
            settings.eveara_user_id = response["uuid"]
            settings.save()

        return settings
    return None
