"""
routers/upload.py
-----------------
File upload route: ``POST /api/upload``.

Accepts a single multipart file, enforces a 200 MB maximum size, saves it under
the local ``uploads/`` directory, and returns a success message.
"""

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api", tags=["Upload"])

# Maximum allowed upload size: 200 MB.
MAX_FILE_SIZE = 200 * 1024 * 1024

# Read the incoming stream in 1 MB chunks so a large file is never held fully in
# memory while we check its size.
CHUNK_SIZE = 1024 * 1024

# Destination directory for stored uploads (created on demand).
UPLOAD_DIR = "uploads"


@router.post(
    "/upload",
    summary="Upload a file (max 200 MB)",
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Upload a single file.

    The file is streamed to disk in chunks; if it exceeds 200 MB the partial
    file is removed and the request is rejected.

    Requires an ``Authorization: Bearer <token>`` header.

    Errors:
      * 400 Bad Request   - no filename supplied
      * 401 Unauthorized  - token missing, invalid, or expired
      * 413 Payload Too Large - file exceeds the 200 MB limit
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided.",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Prefix with a UUID to avoid collisions/overwrites between uploads.
    stored_name = f"{uuid.uuid4().hex}_{os.path.basename(file.filename)}"
    dest_path = os.path.join(UPLOAD_DIR, stored_name)

    size = 0
    try:
        with open(dest_path, "wb") as buffer:
            while chunk := await file.read(CHUNK_SIZE):
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File too large. Maximum allowed size is 200 MB.",
                    )
                buffer.write(chunk)
    except HTTPException:
        # Remove the partially written file before propagating the error.
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise
    finally:
        await file.close()

    return {
        "message": "File uploaded successfully.",
        "filename": file.filename,
        "stored_as": stored_name,
        "size_bytes": size,
    }
