import datetime
import os

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')


DEFAULT_FILE_STORAGE = 'gocreate.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'gocreate.aws.utils.StaticRootS3BotoStorage'

AWS_DEFAULT_ACL = "public-read"

AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
AWS_QUERYSTRING_AUTH = False

# two_months = datetime.timedelta(days=61)
# date_two_months_later = datetime.date.today() + two_months
# expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}


# AWS_HEADERS = {
#     'Expires': expires,
#     'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
# }
