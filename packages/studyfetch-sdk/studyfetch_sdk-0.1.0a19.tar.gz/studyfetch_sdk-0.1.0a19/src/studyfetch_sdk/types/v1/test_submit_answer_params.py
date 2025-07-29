# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TestSubmitAnswerParams"]


class TestSubmitAnswerParams(TypedDict, total=False):
    answer: Required[str]
    """User answer"""

    question_id: Required[Annotated[str, PropertyInfo(alias="questionId")]]
    """Question ID"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID (optional)"""
