# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._types import FileTypes
from ...._utils import PropertyInfo

__all__ = ["ComponentUploadFileParams"]


class ComponentUploadFileParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The file to upload"""

    folder_id: Required[Annotated[str, PropertyInfo(alias="folderId")]]
    """The ID of the folder to upload to"""

    organization_id: Required[Annotated[str, PropertyInfo(alias="organizationId")]]
    """The ID of the organization"""
