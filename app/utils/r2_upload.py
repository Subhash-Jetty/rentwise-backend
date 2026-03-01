import uuid
from werkzeug.utils import secure_filename
import os
from app.utils.r2_client import get_r2_client

def upload_to_r2(file):
    r2 = get_r2_client()

    filename = f"{uuid.uuid4()}-{secure_filename(file.filename)}"
    object_key = f"rentwise-images/{filename}"   # KEEP THIS

    r2.upload_fileobj(
        file,
        os.environ.get("R2_BUCKET_NAME"),
        object_key,
        ExtraArgs={"ContentType": file.content_type}
    )

    return f"{os.environ.get('R2_PUBLIC_URL')}/{object_key}"