# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FlashcardGetAllParams"]


class FlashcardGetAllParams(TypedDict, total=False):
    group_ids: Annotated[str, PropertyInfo(alias="groupIds")]
    """Group IDs (comma-separated)"""

    limit: float
    """Max number of cards"""

    offset: float
    """Offset"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID"""
