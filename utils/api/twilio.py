import os
import base64
from datetime import datetime, timedelta

import pyotp
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from accounts.models import OTP

from twilio.rest import Client

TOKEN_KEY = settings.SECRET_KEY

account_sid = os.getenv('TWILIO_SID', settings.TWILIO_SID)
auth_token = os.getenv('TWILIO_AUTH_TOKEN', settings.TWILIO_AUTH_TOKEN)
TwilioNumber = os.getenv('TWILIO_SENDER_NUMBER',
                         settings.TWILIO_SENDER_NUMBER)


class generateKey:
    @staticmethod
    def returnValue(phone):
        return str(phone) + str(datetime.date(datetime.now())) + TOKEN_KEY


def register_phone(phone, message=None):
    tstamp = timezone.now()
    expiry = tstamp + timedelta(minutes=5.30)
    try:
        mobile = OTP.objects.get(phone=phone)
    except ObjectDoesNotExist:
        mobile = OTP.objects.create(
            phone=phone,
            expiry=expiry
        )

    mobile.expiry = expiry
    mobile.counter += 1
    mobile.save()

    keygen = generateKey()
    key = base64.b32encode(keygen.returnValue(
        phone).encode())  # Key is generated
    otp = pyotp.HOTP(key)  # HOTP Model for OTP is created
    token = otp.at(mobile.counter)

    message = f'''<#>{message} {token}''' if message is not None else f'''<#> {token} is your Gocreate activation code. '''
    message += 'Expires in 5 minutes'

    client = Client(account_sid, auth_token)

    client.messages.create(
        to=phone,
        from_=TwilioNumber,
        body=message + u'\U0001f680')
    print(message)


def verify_otp(phone, otp):
    try:
        mobile = OTP.objects.get(phone=phone)
    except Exception as e:
        print(phone)
        return False, 'Invalid Mobile number'

    tstamp = timezone.now()

    if mobile.expiry >= tstamp:
        key = base64.b32encode(generateKey.returnValue(
            phone).encode())  # Generating Key
        hotp = pyotp.HOTP(key)  # HOTP Model
        if hotp.verify(otp, mobile.counter):  # Verifying the OTP
            return True, ''

        return False, 'OTP is invalid!'

    return False, 'OTP has expired'
