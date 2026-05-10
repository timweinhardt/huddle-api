import io
import boto3
from botocore.exceptions import ClientError, BotoCoreError

from app.core.exceptions import S3UploadError


def upload_image_to_s3(
    image_data: io.BytesIO,
    content_type: str,
    bucket_name: str,
    object_key: str,
    aws_region: str = "us-east-2",
) -> str:
    s3_client = boto3.client("s3", region_name=aws_region)
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=image_data,
            ContentType=content_type,
            ACL="public-read",
        )
    except (ClientError, BotoCoreError) as err:
        raise S3UploadError(f"S3 upload failed: {str(err)}") from err

    url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{object_key}"
    return url
