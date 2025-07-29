# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ScenarioSubmitAnswerParams"]


class ScenarioSubmitAnswerParams(TypedDict, total=False):
    conversation_history: Required[Annotated[Iterable[object], PropertyInfo(alias="conversationHistory")]]
    """Conversation history"""

    final_answer: Annotated[str, PropertyInfo(alias="finalAnswer")]
    """Final answer for the scenario"""
