# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DataAnalystStreamParams", "Message"]


class DataAnalystStreamParams(TypedDict, total=False):
    context: object

    group_id: Annotated[str, PropertyInfo(alias="groupId")]

    messages: Iterable[Message]

    user_id: Annotated[str, PropertyInfo(alias="userId")]

    x_component_id: Annotated[str, PropertyInfo(alias="x-component-id")]


class Message(TypedDict, total=False):
    content: str

    role: Literal["user", "assistant", "system"]
