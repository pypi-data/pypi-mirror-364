# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ScenarioUpdateParams"]


class ScenarioUpdateParams(TypedDict, total=False):
    name: Required[str]
    """Scenario name"""

    characters: Iterable[object]
    """Scenario characters"""

    context: str
    """Scenario context"""

    description: str
    """Scenario description"""

    final_answer_prompt: Annotated[str, PropertyInfo(alias="finalAnswerPrompt")]
    """Prompt for final answer"""

    format: str
    """Interaction format"""

    goal: str
    """Scenario goal"""

    greeting_character_id: Annotated[str, PropertyInfo(alias="greetingCharacterId")]
    """Character ID for greeting"""

    greeting_message: Annotated[str, PropertyInfo(alias="greetingMessage")]
    """Greeting message"""

    requires_final_answer: Annotated[bool, PropertyInfo(alias="requiresFinalAnswer")]
    """Whether scenario requires a final answer"""

    tools: Iterable[object]
    """Available tools"""
