# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["UploadCompleteUploadParams"]


class UploadCompleteUploadParams(TypedDict, total=False):
    material_id: Required[Annotated[str, PropertyInfo(alias="materialId")]]
    """The ID of the material that was uploaded"""

    organization_id: Required[Annotated[str, PropertyInfo(alias="organizationId")]]
    """The ID of the organization"""

    s3_key: Required[Annotated[str, PropertyInfo(alias="s3Key")]]
    """The S3 key of the uploaded file"""
