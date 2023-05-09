import os
import json
import requests

from django.conf import settings

from django_q.tasks import async_task

# from payouts.tasks import pay


PAYSTACK_LIVE_SECRET_KEY = os.getenv(
    'PAYSTACK_LIVE_SECRET_KEY', settings.PAYSTACK_LIVE_SECRET_KEY)
PAYSTACK_TEST_SECRET_KEY = os.getenv(
    'PAYSTACK_TEST_SECRET_KEY', settings.PAYSTACK_TEST_SECRET_KEY
)


def validate_bvn(first_name, last_name, bvn, account_number, middle_name, bank_code):

    lookup_api_url = 'https://api.paystack.co/bvn/match'
    headers = {
        'Authorization': f'Bearer {PAYSTACK_LIVE_SECRET_KEY}',
        'content-type': 'application/json'
    }
    request_data = {
        'bvn': bvn,
        'account_number': account_number,
        'bank_code': bank_code,
        'first_name': first_name,
        'last_name': last_name,
        'middle_name': middle_name
    }

    r = requests.post(lookup_api_url, data=json.dumps(
        request_data), headers=headers)

    response_format = {
        'status': True,
        'message': 'BVN lookup successful',
        'data': {
            'bvn': "000000000000",
            'is_blacklisted': False,
            'account_number': True,
            'first_name': True,
            'last_name': True
        },
        'meta': {
            'calls_this_month': 1,
            'free_calls_left': 9
        }
    }

    response_format = r.json()

    print(response_format)

    importants_look_ups = ['account_number']
    status, msg = response_format['status'], response_format['message']

    try:
        is_blacklisted = response_format['data']['is_blacklisted']
    except KeyError:
        is_blacklisted = False

    if response_format['status']:
        if not is_blacklisted:
            for l in importants_look_ups:
                if not response_format['data'][l]:
                    msg = f'Your BVN details does not match the bio data or account number provided.'
                    status = False
                    return status, msg
            return status, msg

        msg = f'The BVN Provided has been blacklisted.'
        status = False
        return status, msg

    return status, msg


def verify_transactions(reference, amount):
    lookup_api_url = 'https://api.paystack.co/transaction/verify/'+reference
    headers = {
        'Authorization': f'Bearer {PAYSTACK_LIVE_SECRET_KEY}',
        'content-type': 'application/json'
    }

    r = requests.get(lookup_api_url, headers=headers)

    response = r.json()

    status, msg = False, None

    print(response)
    if response.get('status'):
        data = response['data']
        amount_paid = data['amount']
        successful = response['data']['log']['success']
        if successful and amount_paid >= amount:
            status = True
        else:
            status = False
            msg = 'Incorrect amount' if amount_paid >= amount else 'Transaction is not valid'
    else:
        status = response.get('status')
        msg = response.get('message')
    return status, msg


def create_recipient(bank_account=None, royalty_profile=None):
    account = bank_account if bank_account is not None else royalty_profile

    lookup_api_url = 'https://api.paystack.co/transferrecipient'
    headers = {
        'Authorization': f'Bearer {PAYSTACK_LIVE_SECRET_KEY}',
        'content-type': 'application/json'
    }
    request_data = {"type": "nuban",
                    "name": str(account),
                    "description": "Gocreate Royalty",
                    "account_number": account.account_number,
                    "bank_code": account.bank_code,
                    "currency": "NGN"
                    }

    r = requests.post(lookup_api_url, data=json.dumps(
        request_data), headers=headers)

    response = r.json()

    if response['status']:
        recipient_code = response['data']['recipient_code']
        account.recipient_code = recipient_code
        account.save()


def make_transfer(transfer_info):
    lookup_api_url = 'https://api.paystack.co/transfer'
    headers = {
        'Authorization': f'Bearer {PAYSTACK_LIVE_SECRET_KEY}',
        'content-type': 'application/json'
    }

    r = requests.post(lookup_api_url, data=json.dumps(
        transfer_info), headers=headers)

    response = r.json()

    status, result = False, None

    if response['status']:
        transfer_code = response['data']['transfer_code']
        status = True
        result = response['data']

    return status, result


def initiate_bulk(transfer_info):
    lookup_api_url = 'https://api.paystack.co/transfer/bulk'
    headers = {
        'Authorization': f'Bearer {PAYSTACK_LIVE_SECRET_KEY}',
        'content-type': 'application/json'
    }

    r = requests.post(lookup_api_url, data=json.dumps(
        transfer_info), headers=headers)

    response = r.json()

    status, result = False, None
    if response['status']:
        status = True
        result = response['data']
    else:
        result = response['message']

    return status, result


def verify_transfers(payout, index=None):
    lookup_api_url = 'https://api.paystack.co/transfer/verify/'+payout.transaction_id
    headers = {
        'Authorization': f'Bearer {PAYSTACK_LIVE_SECRET_KEY}',
        'content-type': 'application/json'
    }

    r = requests.get(lookup_api_url, headers=headers)

    response = r.json()

    pay_due = None
    if hasattr(payout, 'pay_due'):
        pay_due = payout.pay_due

    if response.get('status'):

        data = response['data']
        if data.get('status') == 'success':
            print(data)
            payout.failed = False
            payout.paid = True
            payout.is_processing = False
            payout.save()

            if pay_due is not None and index == 0:
                async_task('payouts.tasks.update_payout_history', pay_due)

        elif data.get('status') != 'pending':
            payout.failed = True
            payout.paid = False
            payout.is_processing = False
            payout.save()
    else:
        payout.failed = True
        payout.paid = False
        payout.is_processing = False
        payout.save()
