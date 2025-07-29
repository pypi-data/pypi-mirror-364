# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .user import (
    UserResource,
    AsyncUserResource,
    UserResourceWithRawResponse,
    AsyncUserResourceWithRawResponse,
    UserResourceWithStreamingResponse,
    AsyncUserResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["SubmissionsResource", "AsyncSubmissionsResource"]


class SubmissionsResource(SyncAPIResource):
    @cached_property
    def user(self) -> UserResource:
        return UserResource(self._client)

    @cached_property
    def with_raw_response(self) -> SubmissionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SubmissionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SubmissionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return SubmissionsResourceWithStreamingResponse(self)


class AsyncSubmissionsResource(AsyncAPIResource):
    @cached_property
    def user(self) -> AsyncUserResource:
        return AsyncUserResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSubmissionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSubmissionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSubmissionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncSubmissionsResourceWithStreamingResponse(self)


class SubmissionsResourceWithRawResponse:
    def __init__(self, submissions: SubmissionsResource) -> None:
        self._submissions = submissions

    @cached_property
    def user(self) -> UserResourceWithRawResponse:
        return UserResourceWithRawResponse(self._submissions.user)


class AsyncSubmissionsResourceWithRawResponse:
    def __init__(self, submissions: AsyncSubmissionsResource) -> None:
        self._submissions = submissions

    @cached_property
    def user(self) -> AsyncUserResourceWithRawResponse:
        return AsyncUserResourceWithRawResponse(self._submissions.user)


class SubmissionsResourceWithStreamingResponse:
    def __init__(self, submissions: SubmissionsResource) -> None:
        self._submissions = submissions

    @cached_property
    def user(self) -> UserResourceWithStreamingResponse:
        return UserResourceWithStreamingResponse(self._submissions.user)


class AsyncSubmissionsResourceWithStreamingResponse:
    def __init__(self, submissions: AsyncSubmissionsResource) -> None:
        self._submissions = submissions

    @cached_property
    def user(self) -> AsyncUserResourceWithStreamingResponse:
        return AsyncUserResourceWithStreamingResponse(self._submissions.user)
