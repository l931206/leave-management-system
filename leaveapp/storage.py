"""Storage backend for persistent leave attachments on Cloudinary.

The backend stores every allowed attachment as a Cloudinary ``raw`` asset so
PDF and image files share one predictable delivery path. Local development
continues to use Django's FileSystemStorage when CLOUDINARY_URL is absent.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.request import urlopen
from uuid import uuid4

from django.core.files.base import ContentFile
from django.core.files.storage import Storage

import cloudinary
import cloudinary.api
import cloudinary.uploader
from cloudinary.exceptions import NotFound
from cloudinary.utils import cloudinary_url


class CloudinaryRawStorage(Storage):
    """Django storage backend for generic persistent attachments."""

    folder = "leave-management/attachments"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The Cloudinary SDK automatically reads CLOUDINARY_URL. Calling
        # config here makes that behavior explicit and ensures HTTPS URLs.
        cloudinary.config(secure=True)

    def _save(self, name, content):
        suffix = Path(name).suffix.lower()
        public_id = f"{self.folder}/{uuid4().hex}{suffix}"

        # UploadedFile objects are file-like. Reset the pointer when possible
        # because validation may already have read part of the file.
        if hasattr(content, "seek"):
            content.seek(0)

        result = cloudinary.uploader.upload(
            content,
            resource_type="raw",
            public_id=public_id,
            overwrite=False,
            invalidate=True,
        )
        return result["public_id"]

    def _open(self, name, mode="rb"):
        if "b" not in mode:
            raise ValueError("Cloudinary attachments can only be opened in binary mode.")
        with urlopen(self.url(name), timeout=20) as response:
            return ContentFile(response.read(), name=Path(name).name)

    def delete(self, name):
        if not name:
            return
        cloudinary.uploader.destroy(
            name,
            resource_type="raw",
            invalidate=True,
        )

    def exists(self, name):
        if not name:
            return False
        try:
            cloudinary.api.resource(name, resource_type="raw", type="upload")
            return True
        except NotFound:
            return False

    def url(self, name):
        if not name:
            return ""
        url, _ = cloudinary_url(name, resource_type="raw", secure=True)
        return url

    def size(self, name):
        resource = cloudinary.api.resource(name, resource_type="raw", type="upload")
        return int(resource.get("bytes", 0))

    def get_available_name(self, name, max_length=None):
        # _save always creates a UUID-based public ID, so collisions are not
        # possible and no preflight API request is needed.
        return name
