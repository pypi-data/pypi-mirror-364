# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["ComponentGetPresignedURLResponse"]


class ComponentGetPresignedURLResponse(BaseModel):
    key: str
    """The S3 key for the file"""

    upload_url: str = FieldInfo(alias="uploadUrl")
    """The presigned URL for uploading"""
