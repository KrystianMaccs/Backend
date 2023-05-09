from django.conf import settings

import boto3
import pandas as pd
from io import StringIO

from accounts.models import Artist

bucket = settings.AWS_STORAGE_BUCKET_NAME

ACCESS_ID = settings.AWS_ACCESS_KEY_ID
ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY


def update_artist_data():
    data = Artist.objects.values(
        'email', 'first_name', 'last_name', 'phone', 'stage_name').all()

    df = pd.DataFrame(data)

    csv_buffer = StringIO()
    df.to_csv(csv_buffer)

    s3 = boto3.resource('s3',
                        aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=ACCESS_KEY)

    s3.Object(bucket, 'gocreate_artist_fulldata.csv').put(Body=csv_buffer.getvalue())
