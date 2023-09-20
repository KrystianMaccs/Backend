import datetime
from gocreate.settings.base import *

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")

DEFAULT_FILE_STORAGE = 'gocreate.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'gocreate.aws.utils.StaticRootS3BotoStorage'

AWS_DEFAULT_ACL = 'public-read'

AWS_STORAGE_BUCKET_NAME = 'gocreateafrica'
S3DIRECT_REGION = 'us-west-2'
S3_URL = '//%s.s3-accelerate.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3-accelerate.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = {
    'Expires': expires,
    'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}
