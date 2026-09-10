import uuid
import os
import tempfile

import boto3

from config.settings import settings


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)


# ==================================================
# UPLOAD FILE TO S3
# ==================================================

def upload_file_to_s3(
    file_stream,
    filename: str,
    audience: str
):

    extension = filename.rsplit(".", 1)[-1].lower()

    unique_filename = (
        f"{uuid.uuid4()}.{extension}"
    )

    # ----------------------------------------------
    # S3 STRUCTURE
    #
    # documents/buyer/<uuid>.pdf
    # documents/seller/<uuid>.pdf
    # ----------------------------------------------

    s3_key = (
        f"documents/{audience}/{unique_filename}"
    )

    file_stream.seek(0)

    s3_client.upload_fileobj(
        file_stream,
        settings.AWS_BUCKET_NAME,
        s3_key,
        ExtraArgs={
            "Metadata": {
                "original_filename": filename,
                "audience": audience
            }
        }
    )

    return {
        "s3_key": s3_key,
        "original_filename": filename,
        "stored_filename": unique_filename,
        "audience": audience
    }


# ==================================================
# DOWNLOAD DOCUMENT FROM S3
# ==================================================

def download_document_from_s3(s3_key: str):

    extension = os.path.splitext(s3_key)[1]

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=extension
    )

    temp_file.close()

    s3_client.download_file(
        settings.AWS_BUCKET_NAME,
        s3_key,
        temp_file.name
    )

    return temp_file.name


# ==================================================
# DELETE DOCUMENT FROM S3
# ==================================================

def delete_document_from_s3(s3_key: str):

    s3_client.delete_object(
        Bucket=settings.AWS_BUCKET_NAME,
        Key=s3_key
    )

    return True


# ==================================================
# LIST DOCUMENTS
# ==================================================

def list_documents(audience: str = None):

    prefix = "documents/"

    if audience:
        prefix = f"documents/{audience}/"

    response = s3_client.list_objects_v2(
        Bucket=settings.AWS_BUCKET_NAME,
        Prefix=prefix
    )

    return [
        obj["Key"]
        for obj in response.get("Contents", [])
    ]