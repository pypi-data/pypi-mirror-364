# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ExplainerHandleWebhookParams", "Video"]


class ExplainerHandleWebhookParams(TypedDict, total=False):
    event: Required[Literal["video.completed", "video.progress", "video.failed"]]
    """Webhook event type"""

    video: Required[Video]
    """Video data"""


class Video(TypedDict, total=False):
    id: Required[str]
    """Video ID"""

    image_sources: Annotated[object, PropertyInfo(alias="imageSources")]
    """Image sources"""

    progress: float
    """Progress percentage"""

    sections: List[str]
    """Video sections"""

    stream_id: Annotated[str, PropertyInfo(alias="streamId")]
    """Stream ID"""

    stream_url: Annotated[str, PropertyInfo(alias="streamUrl")]
    """Stream URL"""

    thumbnail_url: Annotated[str, PropertyInfo(alias="thumbnailUrl")]
    """Thumbnail URL"""

    transcript: str
    """Video transcript"""

    video_url: Annotated[str, PropertyInfo(alias="videoUrl")]
    """Video URL"""

    web_search_results: Annotated[object, PropertyInfo(alias="webSearchResults")]
    """Web search results"""

    web_search_sources: Annotated[object, PropertyInfo(alias="webSearchSources")]
    """Web search sources"""
