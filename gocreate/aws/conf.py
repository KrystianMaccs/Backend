import datetime
import os

AWS_ACCESS_KEY_ID = "AKIA6ONUY5ZBNTOHVEY3"
AWS_SECRET_ACCESS_KEY = "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"


DEFAULT_FILE_STORAGE = 'gocreate.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'gocreate.aws.utils.StaticRootS3BotoStorage'

AWS_DEFAULT_ACL = None

AWS_STORAGE_BUCKET_NAME = "gocreatestatic"
AWS_S3_REGION_NAME = "us-east-2"
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
# AWS4-HMAC-SHA256 authorization mechanism
# AWS_S3_SIGNATURE_VERSION = 's3v4'
