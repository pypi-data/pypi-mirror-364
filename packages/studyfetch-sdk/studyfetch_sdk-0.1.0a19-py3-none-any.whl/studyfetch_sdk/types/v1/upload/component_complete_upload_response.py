# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["ComponentCompleteUploadResponse"]


class ComponentCompleteUploadResponse(BaseModel):
    id: str
    """The ID of the uploaded material"""

    name: str
    """The name of the material"""

    status: str
    """The status of the material"""
