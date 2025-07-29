# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FlashcardRateParams"]


class FlashcardRateParams(TypedDict, total=False):
    card_id: Required[Annotated[str, PropertyInfo(alias="cardId")]]
    """Flashcard ID"""

    rating: Required[float]
    """Rating (0-3)"""

    group_id: Annotated[str, PropertyInfo(alias="groupId")]
    """Group ID (optional)"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID (optional)"""
