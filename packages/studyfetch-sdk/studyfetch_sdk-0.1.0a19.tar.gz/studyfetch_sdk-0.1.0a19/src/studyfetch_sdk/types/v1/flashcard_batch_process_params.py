# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FlashcardBatchProcessParams", "Operation"]


class FlashcardBatchProcessParams(TypedDict, total=False):
    operations: Required[Iterable[Operation]]

    group_id: Annotated[str, PropertyInfo(alias="groupId")]
    """Group ID (optional)"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID (optional)"""


class Operation(TypedDict, total=False):
    action: Required[Literal["rate", "get_due", "get_all", "get_stats"]]

    card_id: Required[Annotated[str, PropertyInfo(alias="cardId")]]
    """Flashcard ID"""

    group_id: Annotated[str, PropertyInfo(alias="groupId")]
    """Group ID (optional)"""

    rating: float
    """Rating for rate action (0-3)"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID (optional)"""
