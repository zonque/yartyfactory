import boto3
from .config import settings
from typing import BinaryIO

class Storage:
    def __init__(self):
        self.s3_client = boto3.client("s3")

    def path_for_key(self, key: str) ->str :
        return f"{key[0:2]}/{key[2:4]}/{key[5:]}"

    def upload(self, file: BinaryIO, key: str, content_type: str):
        extra_args = {'ContentType': content_type }
        self.s3_client.upload_fileobj(file, settings.STORAGE_S3_BUCKET, self.path_for_key(key), ExtraArgs=extra_args)

    def delete(self, key: str):
        self.s3_client.delete_object(Bucket=settings.STORAGE_S3_BUCKET, Key=self.path_for_key(key))

storage = Storage()
