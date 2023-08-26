import datetime
import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "AKIA6FO2XNP7QHJAX3FQ")
AWS_SECRET_ACCESS_KEY = os.getenv(
    "AWS_SECRET_ACCESS_KEY", "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")

DEFAULT_FILE_STORAGE = 'gocreate.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'gocreate.aws.utils.StaticRootS3BotoStorage'

AWS_DEFAULT_ACL = 'public-read'

AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_ACCESS_KEY_ID", "AKIA6FO2XNP7QHJAX3FQ")
S3DIRECT_REGION = 'us-west-2'
S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
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
