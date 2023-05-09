from .conf import *
from .settings import getUserId
from .authentications import authenticated_header



def get_subscriptions():
    headers = authenticated_header()
    r = requests.get(f'{URL}/subscriptions/get', headers=headers)
    response = r.json()
    data = response.get('data', None)

    if data is not None and len(data) > 0:
        subscriptionId = data[0]['subscriptionId']
        return subscriptionId

    return None


def create_artist_subscription(artist_sub):
    print('Creating eveara subscription')
    headers = authenticated_header()

    artist = artist_sub.artist
    subscriptionId = get_subscriptions()

    if subscriptionId is None:
        raise ValueError("Eveara Subscription ID is none")

    request_data = {
        "uuid": getUserId(),
        "subscriptions":    [
            {
                "subscriptionId": subscriptionId,
                "partnerReferenceId": artist.stage_name
            }
        ]
    }

    r = requests.post(f'{URL}/mySubscriptions/add',
                      data=json.dumps(request_data), headers=headers)

    response = r.json()
    if not response['success']:
        raise ValueError(f"Eveara: {response['message']}")

    data = response.get('data', None)
    if data is not None and len(data) > 0:
        subscriptionId = data[0]['mySubscriptionId']
        artist_sub.eveara_id = subscriptionId
        artist_sub.activated = True
        artist_sub.save()

        print('Eveara Album Successfully created')


def reactivate_artist_subscription(artist_sub):
    print('Reactivating eveara Subscription')
    headers = authenticated_header()

    request_data = {
        "uuid": getUserId(),
        "mySubscriptionId":   artist_sub.eveara_id
    }

    r = requests.post(f'{URL}/mySubscriptions/reactivate',
                      data=json.dumps(request_data), headers=headers)

    response = r.json()
    if not response['success']:
        raise ValueError(f"Eveara: {response['message']}")

    artist_sub.activated = True
    artist_sub.save()

    print('Eveara Subscription Reactivation Success')


def deactivate_artist_subscription(artist_sub):
    print('Deactivating eveara subscription')
    headers = authenticated_header()

    request_data = {
        "uuid": getUserId(),
        "mySubscriptionId":   artist_sub.eveara_id
    }

    r = requests.post(f'{URL}/mySubscriptions/deactivate',
                      data=json.dumps(request_data), headers=headers)

    response = r.json()
    if not response['success']:
        raise ValueError(f"Eveara: {response['message']}")

    artist_sub.activated = False
    artist_sub.save()

    print('Eveara Subscription deactivation Success')
