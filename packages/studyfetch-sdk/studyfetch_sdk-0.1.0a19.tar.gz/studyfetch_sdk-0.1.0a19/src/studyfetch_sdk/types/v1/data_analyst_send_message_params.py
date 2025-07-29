# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DataAnalystSendMessageParams", "Message", "MessageImage"]


class DataAnalystSendMessageParams(TypedDict, total=False):
    component_id: Required[Annotated[str, PropertyInfo(alias="componentId")]]
    """Component ID for context"""

    message: Required[Message]
    """Chat message content"""

    x_component_id: Required[Annotated[str, PropertyInfo(alias="x-component-id")]]

    context: object
    """Additional context data"""

    group_ids: Annotated[List[str], PropertyInfo(alias="groupIds")]
    """Group IDs for collaboration"""

    session_id: Annotated[str, PropertyInfo(alias="sessionId")]
    """Session ID for conversation continuity"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID for tracking"""


class MessageImage(TypedDict, total=False):
    base64: str
    """Base64 encoded image data"""

    caption: str
    """Caption for the image"""

    mime_type: Annotated[str, PropertyInfo(alias="mimeType")]
    """MIME type of the image"""

    url: str
    """URL of the image"""


class Message(TypedDict, total=False):
    images: Iterable[MessageImage]
    """Images attached to the message"""

    text: str
    """Text content of the message"""
