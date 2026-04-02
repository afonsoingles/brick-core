import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

class Storage:
    def __init__(self):
        session = boto3.Session(
            aws_access_key_id=os.environ.get("S3_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY"),
        )
        self.s3 = session.client(
            "s3",
            endpoint_url=os.environ.get("S3_ENDPOINT_URL"),
            config=Config(signature_version='s3v4')
        )
    
    def generate_presigned_url(self, bucket, key, expiration=3600):
        url = self.s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket,
                "Key": key
            },
            ExpiresIn=expiration,
            HttpMethod="GET"
        )

        return url

    def upload_file(self, bucket, key, content):
        upload = self.s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=content
        )
        return upload
    
    def get_file_data(self, bucket, key):
        obj = self.s3.get_object(Bucket=bucket, Key=key)
        return obj["Body"].read()