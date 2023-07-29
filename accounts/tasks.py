import random
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.utils import timezone
from django.conf import settings
import requests
import json
import six
import os

from .models import Artist

from datetime import datetime, timedelta


from .models import Artist

EMAIL_HOST = 'noreply@gocreateafrica.app'

User = get_user_model()


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()


def confirm_email(params):
    current_site, pk = params['domain'], params['pk']
    artist = Artist.objects.get(pk=pk)
    mail_subject = 'Activate your GoCreate account.'
    encode_details = mail_encoded_body(artist)
    uid = urlsafe_base64_encode(force_bytes(
        json.dumps(encode_details, cls=DjangoJSONEncoder)))
    token = account_activation_token.make_token(artist)
    print("uid ", uid)
    print("token ", token)
    message = render_to_string('accounts/acc_active_email.html', {
        'user': artist,
        'domain': current_site.domain,
        'uid': uid,
        'token': token,
    })
    send_email(mail_subject, message, artist.email)


def confirm_reset_password(params):
    current_site, pk = params['domain'], params['pk']
    user = None

    if params['artist']:
        user = Artist.objects.get(pk=pk)
    else:
        user = User.objects.get(pk=pk)

    mail_subject = 'Reset your GoCreate password.'
    encode_details = mail_encoded_body(user)
    uid = urlsafe_base64_encode(force_bytes(
        json.dumps(encode_details, cls=DjangoJSONEncoder)))
    token = account_activation_token.make_token(user)
    print("uid ", uid)
    print("token ", token)
    message = render_to_string('accounts/reset_password.html', {
        'user': user,
        'domain': current_site,
        'uid': uid,
        'token': token
    })
    send_email(mail_subject, message, user.email)


def verify_artist_email(uidb64, token):
    try:
        decoded_content = force_str(urlsafe_base64_decode(uidb64))
        content = json.loads(decoded_content)

        try:
            user = Artist.objects.get(email=content['pk'])
        except Artist.DoesNotExsit:
            user = User.objects.get(email=content['pk'])
        except User.DoesNotExsit:
            user = None

    except Exception as e:
        user = None

    if user is not None and user.is_active:
        return user, account_activation_token.check_token(user, token)

    return user, user is not None


def mail_encoded_body(user):
    return {
        'pk': user.email,
        'assignment_timestamp': timezone.now()
    }


def send_email(mail_subject, message, to_email):

    email = EmailMessage(
        mail_subject, message, from_email=EMAIL_HOST, to=[
            to_email,
            # 'bellotobiloba01@gmail.com',
            # 'ifetola.agbesanwa@maitechstudio.net',
            # 'iyiolaema@gmail.com',
            # 'akinstiles349@gmail.com',
            # 'ifetola@outlook.com',
            # 'ojigboo@gmail.com',
        ]
    )

    email.content_subtype = 'html'
    email.send()
