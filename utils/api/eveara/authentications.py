from django.utils import timezone
from datetime import timedelta
import requests
import json

from .conf import (
    URL,
    EVEARA_CLIENT_ID,
    EVEARA_CLIENT_SECRET
)

AUTHORIZATION = {
    'access_token': None,
    'expiry': None,
    'token_type': None
}

def is_expired():
    expired = True

    expiry = AUTHORIZATION['expiry']
    tstamp = timezone.now()

    if expiry is not None:
        if expiry >= tstamp:
            expired = False

    return expired


def get_headers():
    headers = {
        'content-type': 'application/json'
    }

    is_authenticated = False

    if AUTHORIZATION['access_token'] is not None and not is_expired():
        headers['Authorization'] = f'{AUTHORIZATION["token_type"]} {AUTHORIZATION["access_token"]}'
        is_authenticated = True

    return headers, is_authenticated


def authenticated_header():
    headers, is_authenticated = get_headers()

    if not is_authenticated:

        request_data = {
            "grant_type": "client_credentials",
            "client_id": EVEARA_CLIENT_ID,
            "client_secret": EVEARA_CLIENT_SECRET
        }

        r = requests.post(f'{URL}/oauth/gettoken', data=json.dumps(
            request_data), headers=headers)

        response = r.json()
        print(response)

        if response['success']:
            AUTHORIZATION['access_token'] = response['access_token']
            AUTHORIZATION['expiry'] = timezone.now(
            ) + timedelta(seconds=response['expires_in'])
            AUTHORIZATION['token_type'] = response['token_type']

    return get_headers()[0]
