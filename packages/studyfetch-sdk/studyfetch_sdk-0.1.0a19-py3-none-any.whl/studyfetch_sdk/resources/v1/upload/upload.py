# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .component import (
    ComponentResource,
    AsyncComponentResource,
    ComponentResourceWithRawResponse,
    AsyncComponentResourceWithRawResponse,
    ComponentResourceWithStreamingResponse,
    AsyncComponentResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["UploadResource", "AsyncUploadResource"]


class UploadResource(SyncAPIResource):
    @cached_property
    def component(self) -> ComponentResource:
        return ComponentResource(self._client)

    @cached_property
    def with_raw_response(self) -> UploadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return UploadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UploadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return UploadResourceWithStreamingResponse(self)


class AsyncUploadResource(AsyncAPIResource):
    @cached_property
    def component(self) -> AsyncComponentResource:
        return AsyncComponentResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncUploadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUploadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUploadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncUploadResourceWithStreamingResponse(self)


class UploadResourceWithRawResponse:
    def __init__(self, upload: UploadResource) -> None:
        self._upload = upload

    @cached_property
    def component(self) -> ComponentResourceWithRawResponse:
        return ComponentResourceWithRawResponse(self._upload.component)


class AsyncUploadResourceWithRawResponse:
    def __init__(self, upload: AsyncUploadResource) -> None:
        self._upload = upload

    @cached_property
    def component(self) -> AsyncComponentResourceWithRawResponse:
        return AsyncComponentResourceWithRawResponse(self._upload.component)


class UploadResourceWithStreamingResponse:
    def __init__(self, upload: UploadResource) -> None:
        self._upload = upload

    @cached_property
    def component(self) -> ComponentResourceWithStreamingResponse:
        return ComponentResourceWithStreamingResponse(self._upload.component)


class AsyncUploadResourceWithStreamingResponse:
    def __init__(self, upload: AsyncUploadResource) -> None:
        self._upload = upload

    @cached_property
    def component(self) -> AsyncComponentResourceWithStreamingResponse:
        return AsyncComponentResourceWithStreamingResponse(self._upload.component)
