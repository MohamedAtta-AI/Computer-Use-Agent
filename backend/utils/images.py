import os
import uuid
import base64
import hashlib

def save_screenshot_and_return_url(base64_data: str) -> str:
    """
    Saves base64 PNG screenshot to disk and returns its public URL path.
    """
    os.makedirs("uploads", exist_ok=True)
    image_data = base64.b64decode(base64_data)

    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}.png"

    with open(file_path, "wb") as f:
        f.write(image_data)

    return f"/uploads/{file_id}.png"


def compute_sha256(data: bytes | str) -> str:
    """
    Computes SHA-256 hash of binary data or a base64 string.
    """
    if isinstance(data, str):
        data = base64.b64decode(data)
    return hashlib.sha256(data).hexdigest()
