from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils import timezone
import json
import six

from accounts.tasks import send_email, mail_encoded_body, account_activation_token
from .models import Royalty


def get_verififcation_details(request, royalty, song):
    return {
        'domain': get_current_site(request),
        'artist': request.user,
        'song': song,
        'royalty': royalty
    }


def get_or_create_royalty(royalty_data):
    status = False
    try:
        royalty = Royalty.objects.get(
            username=royalty_data['email'])

        royalty.phone = royalty_data['phone']
        royalty.save()

    except Royalty.DoesNotExist:
        royalty = Royalty.objects.create(
            username=royalty_data['email'], phone=royalty_data['phone'])
        status = True

    return royalty, status


def get_or_create_royalties(request, royalties, song_title):
    royalty = None
    returned_royalties = []

    for r in royalties:

        royalty, created = get_or_create_royalty(royalty)
        returned_royalties.append(royalty)

        confirm_royalty_mail(get_verififcation_details(
            request, r, song_title))

    return returned_royalties


def confirm_royalty_mail(params):
    current_site = params['domain']

    royalty = params['royalty']
    email = royalty['email']
    artist = params['artist']
    song = params['song']

    mail_subject = 'Royalty from Gocreate'
    encode_details = {
        'pk': email,
        'song': str(song.id),
        'split_id': royalty['id'],
        'assignment_timestamp': str(timezone.now())
    }
    uid = urlsafe_base64_encode(force_bytes(json.dumps(encode_details)))
    token = account_activation_token.make_token(artist)

    message = render_to_string('royalty/royalty.html', {
        'title': mail_subject,
        'fullname': royalty['fullname'],
        "description": royalty['description'],
        'artist': artist,
        "share": royalty['share'],
        'song_title': song.title,
        'domain': current_site,
        'uid': uid,
        'token': token,
    })

    print("uid ", uid)
    print("token ", token)
    send_email(mail_subject, message, email)


def verify_royalty_email(uidb64, token):
    content = None
    try:
        decoded_content = force_text(urlsafe_base64_decode(uidb64))
        content = json.loads(decoded_content)

        try:
            user = Royalty.objects.get(username=content['pk'])
        except Royalty.DoesNotExsit:
            user = None

    except Exception as e:
        user = None

    return user, user is not None, content['split_id'] if content is not None else None
