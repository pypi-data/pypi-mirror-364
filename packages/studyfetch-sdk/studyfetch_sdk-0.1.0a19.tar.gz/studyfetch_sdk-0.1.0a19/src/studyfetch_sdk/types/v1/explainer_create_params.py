# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ExplainerCreateParams"]


class ExplainerCreateParams(TypedDict, total=False):
    component_id: Required[Annotated[str, PropertyInfo(alias="componentId")]]
    """Component ID"""

    folder_ids: Required[Annotated[List[str], PropertyInfo(alias="folderIds")]]
    """Folder IDs to include"""

    material_ids: Required[Annotated[List[str], PropertyInfo(alias="materialIds")]]
    """Material IDs to include"""

    target_length: Required[Annotated[float, PropertyInfo(alias="targetLength")]]
    """Target video length in seconds"""

    title: Required[str]
    """Title for the explainer video"""

    image_search: Annotated[bool, PropertyInfo(alias="imageSearch")]
    """Enable image search for visuals"""

    model: str
    """AI model to use"""

    style: str
    """Video style"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID"""

    vertical_video: Annotated[bool, PropertyInfo(alias="verticalVideo")]
    """Create vertical video format (9:16)"""

    web_search: Annotated[bool, PropertyInfo(alias="webSearch")]
    """Enable web search for additional content"""
