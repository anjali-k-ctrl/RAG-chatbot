import boto3

from config.settings import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

from config.settings import settings
import os


def upload_document_to_s3(file_path: str):

    file_name = os.path.basename(file_path)

    s3_key = f"documents/{file_name}"

    s3_client.upload_file(
        file_path,
        settings.AWS_BUCKET_NAME,
        s3_key
    )

    return s3_key

import tempfile
import os

def download_document_from_s3(s3_key: str):

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".docx"
    )

    temp_file.close()

    s3_client.download_file(
        settings.AWS_BUCKET_NAME,
        s3_key,
        temp_file.name
    )

    return temp_file.name