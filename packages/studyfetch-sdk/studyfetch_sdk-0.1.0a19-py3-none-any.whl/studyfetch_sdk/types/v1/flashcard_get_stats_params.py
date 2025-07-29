# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FlashcardGetStatsParams"]


class FlashcardGetStatsParams(TypedDict, total=False):
    group_ids: Annotated[str, PropertyInfo(alias="groupIds")]
    """Group IDs (comma-separated)"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID"""
