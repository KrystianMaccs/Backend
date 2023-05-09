import hashlib
import time
import base64
import hmac
import datetime
import codecs
import requests  # pip install requests


class DJMApiCall:

    def __init__(self, _key, _secret):
        self.host = "https://djmonitor.com"
        self.http_method = "GET"
        self.url_endpoint = "/api/recognition-platform"

        self.key = _key
        self.secret = _secret

    def CreateAuthenticatedCallData(self, fields={}):

        timestamp = int(time.mktime(
            datetime.datetime.utcfromtimestamp(time.time()).timetuple()))

        string_to_sign = self.http_method+"\n"+self.url_endpoint + \
            "\n"+str(self.key)+"\n"+str(timestamp)
        sign = base64.b64encode(hmac.new(codecs.encode(self.secret), codecs.encode(
            string_to_sign), digestmod=hashlib.sha256).digest())

        fields.update({
            'access_key': self.key,
            'timestamp': timestamp,
            'signature': sign
        })

        return fields


class DJMFingerprintBucket(DJMApiCall):

    def __init__(self, _key, _secret, _bucket_name):
        super(DJMFingerprintBucket, self).__init__(_key, _secret)
        self.bucket_name = _bucket_name

    def add_fingerprint(self, filepath, fingerprint_metadata):
        self.http_method = "POST"
        self.url_endpoint = "/api/recognition-platform/bucket/add-fingerprint"

        fingerprint_metadata.update({
            'bucket': self.bucket_name
        })

        files = {'audio_file': open(filepath, 'rb')}

        request_data = self.CreateAuthenticatedCallData(fingerprint_metadata)
        server_url = self.host + self.url_endpoint

        try:
            resp = requests.post(server_url, files=files,
                                 data=request_data, timeout=60)

        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        return resp.text

    def remove_fingerprint(self, fields):

        self.http_method = "POST"
        self.url_endpoint = "/api/recognition-platform/bucket/delete-fingerprint"

        request_data = self.CreateAuthenticatedCallData(fields)
        server_url = self.host + self.url_endpoint

        try:
            resp = requests.post(server_url, data=request_data, timeout=60)

        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        return resp.text

    def get_fingerprint_plays(self, fields):

        self.http_method = "POST"
        self.url_endpoint = "/api/recognition-platform/bucket/get-fingerprint-plays-for-period"

        request_data = self.CreateAuthenticatedCallData(fields)
        server_url = self.host + self.url_endpoint

        try:
            resp = requests.post(server_url, data=request_data, timeout=60)

        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        return resp.text


class DJMRadioStreams(DJMApiCall):

    def fetch_radio_stream_playlist_for_date(self, fields):

        self.http_method = "POST"
        self.url_endpoint = "/api/recognition-platform/radio-stream/fetch-radio-stream-playlist-for-date"

        request_data = self.CreateAuthenticatedCallData(fields)

        server_url = self.host + self.url_endpoint
        try:
            resp = requests.post(server_url, data=request_data)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        return resp.text

    def edit_radio_stream(self, fields):

        self.http_method = "POST"
        self.url_endpoint = "/api/recognition-platform/radio-stream/edit-radio-stream"

        request_data = self.CreateAuthenticatedCallData(fields)

        server_url = self.host + self.url_endpoint
        try:
            resp = requests.post(server_url, data=request_data)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        return resp.text

    def get_status_of_radio_streams(self):

        self.http_method = "POST"
        self.url_endpoint = "/api/recognition-platform/radio-stream/get-status-of-radio-streams"

        request_data = self.CreateAuthenticatedCallData()

        server_url = self.host + self.url_endpoint
        try:
            resp = requests.post(server_url, data=request_data)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        return resp.text
