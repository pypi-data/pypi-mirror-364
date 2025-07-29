# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FlashcardGetDueParams"]


class FlashcardGetDueParams(TypedDict, total=False):
    group_ids: Required[Annotated[str, PropertyInfo(alias="groupIds")]]

    limit: float
    """Max number of cards"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID"""
