from django.contrib.sites.shortcuts import get_current_site

from datetime import datetime, timedelta, date
from dateutil import parser
import calendar
import uuid
import os

import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def compressImage(image):
    try:
        ext = image.name.split('.').pop()

        if ext == 'jpg':
            return compressJPG(image)
        elif ext == 'png':
            return compressPNG(image)
    except:
        pass

    return image


def redefinedFileName(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(instance.song_dir, filename)


def redefinedSongFileName(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(instance.directory_string_var, filename)


def compressJPG(image):
    outputIoStream = BytesIO()
    imageTemporary = Image.open(image)
    imageTemporaryResized = imageTemporary.resize((1020, 573))

    imageTemporary.save(outputIoStream, format='JPEG', quality=60)
    outputIoStream.seek(0)
    image = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % image.name.split('.')[
        0], 'image/jpg', sys.getsizeof(outputIoStream), None)

    return image


def compressPNG(image):
    outputIoStream = BytesIO()
    imageTemporary = Image.open(image)
    imageTemporaryResized = imageTemporary.convert(
        mode='P', palette=Image.ADAPTIVE)
    imageTemporary.save(outputIoStream, format='PNG',
                        optimize=True, quality=50)
    outputIoStream.seek(0)
    image = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.png" % image.name.split('.')[
        0], 'image/png', sys.getsizeof(outputIoStream), None)

    return image


def resizeImage(image):
    try:
        ext = image.name.split('.').pop()
        if ext == 'jpg':
            return resizeJPG(image)
        elif ext == 'png':
            return resizePNG(image)
    except:
        pass

    return image


def resizeJPG(image):
    outputIoStream = BytesIO()
    imageTemporary = Image.open(image)
    imageTemporaryResized = imageTemporary.resize((1400, 1400))
    imageTemporaryResized.save(outputIoStream, format='JPEG', quality=100)
    outputIoStream.seek(0)
    image = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % image.name.split('.')[
        0], 'image/jpg', sys.getsizeof(outputIoStream), None)

    return image


def resizePNG(image):
    outputIoStream = BytesIO()
    imageTemporary = Image.open(image)
    imageTemporaryResized = imageTemporary.convert(
        mode='P', palette=Image.ADAPTIVE)
    imageTemporaryResized.save(outputIoStream, format='PNG',
                               optimize=True, quality=100)
    outputIoStream.seek(0)
    image = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.png" % image.name.split('.')[
        0], 'image/png', sys.getsizeof(outputIoStream), None)

    return image


def is_leap_year(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


def add_year(date, years):
    if years > 0:
        if is_leap_year(date.year):
            delta = timedelta(days=(366 * years))
        else:
            delta = timedelta(days=(365 * years))

        return date + delta
    return date


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(int(year), int(month), int(day))


def get_next_month_ending(current_date):
    go_to_next = current_date.day >= 20
    next_month = current_date.replace(day=28)
    last_next_month = next_month + timedelta(days=4)

    month = next_month.month if go_to_next else current_date.month

    last_day_of_month = calendar.monthrange(
        next_month.year, next_month.month)[1]

    last_day_of_current = calendar.monthrange(
        current_date.year, current_date.month)[1]

    day = last_day_of_month if go_to_next else last_day_of_current

    return current_date.replace(day=day, month=month)


def secure_domain(domain, request=None):
    return f'https://{domain}' if request is not None and request.is_secure else f'http://{domain}'


def file_url(url, request=None):
    local = 'http://localhost:8000'
    if 'http' in url:
        return url
    else:
        current_site = secure_domain(get_current_site(
            request).domain, request) if request is not None else local
        url = f'{current_site}{url}'

    return url


def value_not_empty(value):
    return value is not None and len(value) > 1


def string2date(date: str):

    return parser.parse(date)


def date2string(date: datetime):
    df = '%Y-%m-%d %H:%M:%S.%f'
    return datetime.strftime(date, df)
