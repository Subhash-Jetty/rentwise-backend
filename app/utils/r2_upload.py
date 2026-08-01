import uuid
import logging
from werkzeug.utils import secure_filename
import os
from app.utils.r2_client import get_r2_client

logger = logging.getLogger(__name__)

def upload_to_r2(file):
    bucket_name = os.environ.get("R2_BUCKET_NAME")
    public_url = os.environ.get("R2_PUBLIC_URL")

    if not bucket_name or not public_url:
        logger.error("R2 configuration missing: R2_BUCKET_NAME or R2_PUBLIC_URL")
        raise ValueError("Server configuration error for image upload.")

    r2 = get_r2_client()

    filename = f"{uuid.uuid4()}-{secure_filename(file.filename)}"
    object_key = f"rentwise-images/{filename}"   # KEEP THIS

    logger.info(f"Attempting to upload {filename} to R2 bucket {bucket_name}")
    try:
        r2.upload_fileobj(
            file,
            bucket_name,
            object_key,
            ExtraArgs={"ContentType": file.content_type}
        )
        logger.info(f"Successfully uploaded {filename} to R2")
        return f"{public_url}/{object_key}"
    except Exception as e:
        logger.error(f"Failed to upload {filename} to R2: {str(e)}")
        raise Exception("Image upload failed.")

def delete_from_r2(image_url):
    bucket_name = os.environ.get("R2_BUCKET_NAME")
    public_url = os.environ.get("R2_PUBLIC_URL")

    if not bucket_name or not public_url:
        logger.error("R2 configuration missing: R2_BUCKET_NAME or R2_PUBLIC_URL")
        raise ValueError("Server configuration error for image deletion.")

    if image_url.startswith(public_url):
        object_key = image_url[len(public_url):].lstrip('/')
    else:
        object_key = image_url

    r2 = get_r2_client()
    logger.info(f"Attempting to delete {object_key} from R2 bucket {bucket_name}")
    try:
        r2.delete_object(Bucket=bucket_name, Key=object_key)
        logger.info(f"Successfully deleted {object_key} from R2")
    except Exception as e:
        logger.error(f"Failed to delete {object_key} from R2: {str(e)}")
        raise Exception("Image deletion failed.")