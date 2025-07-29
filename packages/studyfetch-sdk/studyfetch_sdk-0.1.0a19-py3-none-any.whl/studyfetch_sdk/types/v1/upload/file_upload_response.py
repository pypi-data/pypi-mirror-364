# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["FileUploadResponse"]


class FileUploadResponse(BaseModel):
    id: str
    """The ID of the uploaded material"""

    content_type: str = FieldInfo(alias="contentType")
    """The content type of the material"""

    name: str
    """The name of the material"""

    s3_key: str = FieldInfo(alias="s3Key")
    """The S3 key of the uploaded file"""

    status: str
    """The status of the material"""
