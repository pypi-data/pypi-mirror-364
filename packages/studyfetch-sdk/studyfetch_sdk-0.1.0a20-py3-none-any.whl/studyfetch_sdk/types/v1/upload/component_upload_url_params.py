# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ComponentUploadURLParams"]


class ComponentUploadURLParams(TypedDict, total=False):
    folder_id: Required[Annotated[str, PropertyInfo(alias="folderId")]]
    """The ID of the folder to upload to"""

    name: Required[str]
    """The name for the uploaded file"""

    organization_id: Required[Annotated[str, PropertyInfo(alias="organizationId")]]
    """The ID of the organization"""

    url: Required[str]
    """The URL of the file to upload"""
