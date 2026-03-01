import os
import uuid
from app.utils.r2_client import get_r2_client

def upload_to_r2(file):
    r2 = get_r2_client()

    bucket_name = os.environ.get("R2_BUCKET_NAME")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"

    r2.upload_fileobj(
        file,
        bucket_name,
        unique_filename,
        ExtraArgs={"ContentType": file.content_type}
    )

    return f"{os.environ.get('R2_ENDPOINT_URL')}/{bucket_name}/{unique_filename}"