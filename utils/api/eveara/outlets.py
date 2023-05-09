from systemcontrol.models import Outlet
from .conf import *
from .settings import getUserId
from .authentications import authenticated_header

outlets = []



def get_outlets_api():
    global outlets
    headers = authenticated_header()
    request_data = {
        "UUID": getUserId()
    }

    r = requests.get(f'{URL}/outlets/get?uuid='+getUserId(), headers=headers)

    response = r.json()
    if r.status_code < 300:
        if response['success']:
            data = response['data']
            if len(data) > 0:
                # results = [s['storeId'] for s in data]
                # outlets = results

                return response

                print("Outlet Updated")
        else:
            print("Error from Eveara API", response)
    else:
        print("Eveara API Crashed", response)

    return None


def update_outlets(response):
    Outlet.objects.all().delete()

    data = response.get('data')
    outls = [Outlet(storeId=d['storeId'], storeName=d['storeName'])
             for d in data]
    Outlet.objects.bulk_create(outls)

    return outls


def get_outlets():
    saved_outlets = Outlet.objects.values('storeId').all()
    ol = [v['storeId'] for v in saved_outlets]

    if len(ol) == 0:
        outlet_response = get_outlets_api()
        if outlet_response is not None:
            outlets = update_outlets(outlet_response)
            ol = [o.storeId for o in outlets]

    return ol


def get_song_link(eveara_album_id):
    headers = authenticated_header()

    r = requests.get(f'{URL}/outlets/smartlinks?albumId=' +
                     str(eveara_album_id), headers=headers)

    response = r.json()
    return response
