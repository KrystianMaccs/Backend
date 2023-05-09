import stripe
from django.conf import settings
from django.http import HttpResponse

from accounts.models import Artist
from subscriptions.models import Package
from subscriptions.utils import (
    create_potential_artistsub, activate_potential_artistsub, cancel_potential_artistsub)

# stripe.api_key = settings.STRIPE_LIVE_KEY
PAYMENT_IS_LIVE = str(settings.PAYMENT_IS_LIVE) == '1'
stripe.api_key = settings.STRIPE_LIVE_KEY if PAYMENT_IS_LIVE  else settings.STRIPE_TEST_KEY

test_endpoint_secret = 'whsec_jMqknxDcKP4ecrjdwm3SMlHLPMGPzUrq'
live_endpoint_secret = 'whsec_BWrZhvMPNbM0Uqk8nAVVPKnxZpEH9Piw'

endpoint_secret = live_endpoint_secret if PAYMENT_IS_LIVE  else test_endpoint_secret


def create_payment_intent(artist: Artist, package: Package):
    intent = stripe.PaymentIntent.create(
        amount=int(package.price) * 100,
        currency='usd',
        # Verify your integration in this guide by including this parameter
        metadata={'integration_check': 'accept_a_payment'},
    )

    secret: str = intent.client_secret
    create_potential_artistsub(artist, package, secret)

    return secret


def cancel_payment_intent(client_secret):
    stripe.SetupIntent.cancel(
        client_secret
    )
    cancel_potential_artistsub(client_secret)


# def initialize_transaction(artist: Artist, package: Package, current_domain: str) -> str:

#     success_url: str = ''
#     cancel_url: str = ''
#     success_url = current_domain + success_url,
#     cancel_url = current_domain + cancel_url,

#     print(success_url)
#     print(cancel_url)

#     checkout_session = stripe.checkout.Session.create(
#         payment_method_types=['card'],
#         line_items=[
#             {
#                 'price_data': {
#                     'currency': 'usd',
#                     'unit_amount': package.price,
#                     'product_data': {
#                         'name': package.title,
#                     },
#                 },
#                 'quantity': 1,
#             },
#         ],
#         mode='payment',
#         success_url=success_url,
#         cancel_url=cancel_url,
#     )

#     session_id: str = checkout_session.id

#     create_potential_artistsub(artist, package, session_id)
#     return session_id




def payment_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    client_secret: str = ''

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle Payment Intent
    if event['type'] == 'payment_intent.succeeded':
        session = event['data']['object']

        print('Payment Intent Success ', session)

        client_secret = session['client_secret']
        if session['status'] == "succeeded":
            activate_potential_artistsub(client_secret)

    elif event['type'] == 'payment_intent.canceled' or event['type'] == 'payment_intent.payment_failed':
        session = event['data']['object']

        client_secret = session['client_secret']
        cancel_potential_artistsub(client_secret)
        print('Payment Intent failed ', client_secret)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        print('Completed ', session)
        if session.payment_status == "paid":
            activate_potential_artistsub(session.id)

    elif event['type'] == 'checkout.session.async_payment_succeeded':
        session = event['data']['object']

        activate_potential_artistsub(session.id)
        print('Async Success ', session)
    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']

        print('Async failed ', session)
        cancel_potential_artistsub(session.id)

    return HttpResponse(status=200)
