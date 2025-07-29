# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .sections import (
    SectionsResource,
    AsyncSectionsResource,
    SectionsResourceWithRawResponse,
    AsyncSectionsResourceWithRawResponse,
    SectionsResourceWithStreamingResponse,
    AsyncSectionsResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options

__all__ = ["AudioRecapsResource", "AsyncAudioRecapsResource"]


class AudioRecapsResource(SyncAPIResource):
    @cached_property
    def sections(self) -> SectionsResource:
        return SectionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AudioRecapsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AudioRecapsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AudioRecapsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AudioRecapsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Create a new audio recap"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/api/v1/audio-recaps/create",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve(
        self,
        recap_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get audio recap by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not recap_id:
            raise ValueError(f"Expected a non-empty value for `recap_id` but received {recap_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/audio-recaps/{recap_id}/get",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def ask_question(
        self,
        recap_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Ask a question about the audio recap

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not recap_id:
            raise ValueError(f"Expected a non-empty value for `recap_id` but received {recap_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/audio-recaps/{recap_id}/ask-question",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncAudioRecapsResource(AsyncAPIResource):
    @cached_property
    def sections(self) -> AsyncSectionsResource:
        return AsyncSectionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAudioRecapsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAudioRecapsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAudioRecapsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncAudioRecapsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Create a new audio recap"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/api/v1/audio-recaps/create",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve(
        self,
        recap_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get audio recap by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not recap_id:
            raise ValueError(f"Expected a non-empty value for `recap_id` but received {recap_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/audio-recaps/{recap_id}/get",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def ask_question(
        self,
        recap_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Ask a question about the audio recap

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not recap_id:
            raise ValueError(f"Expected a non-empty value for `recap_id` but received {recap_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/audio-recaps/{recap_id}/ask-question",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AudioRecapsResourceWithRawResponse:
    def __init__(self, audio_recaps: AudioRecapsResource) -> None:
        self._audio_recaps = audio_recaps

        self.create = to_raw_response_wrapper(
            audio_recaps.create,
        )
        self.retrieve = to_raw_response_wrapper(
            audio_recaps.retrieve,
        )
        self.ask_question = to_raw_response_wrapper(
            audio_recaps.ask_question,
        )

    @cached_property
    def sections(self) -> SectionsResourceWithRawResponse:
        return SectionsResourceWithRawResponse(self._audio_recaps.sections)


class AsyncAudioRecapsResourceWithRawResponse:
    def __init__(self, audio_recaps: AsyncAudioRecapsResource) -> None:
        self._audio_recaps = audio_recaps

        self.create = async_to_raw_response_wrapper(
            audio_recaps.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            audio_recaps.retrieve,
        )
        self.ask_question = async_to_raw_response_wrapper(
            audio_recaps.ask_question,
        )

    @cached_property
    def sections(self) -> AsyncSectionsResourceWithRawResponse:
        return AsyncSectionsResourceWithRawResponse(self._audio_recaps.sections)


class AudioRecapsResourceWithStreamingResponse:
    def __init__(self, audio_recaps: AudioRecapsResource) -> None:
        self._audio_recaps = audio_recaps

        self.create = to_streamed_response_wrapper(
            audio_recaps.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            audio_recaps.retrieve,
        )
        self.ask_question = to_streamed_response_wrapper(
            audio_recaps.ask_question,
        )

    @cached_property
    def sections(self) -> SectionsResourceWithStreamingResponse:
        return SectionsResourceWithStreamingResponse(self._audio_recaps.sections)


class AsyncAudioRecapsResourceWithStreamingResponse:
    def __init__(self, audio_recaps: AsyncAudioRecapsResource) -> None:
        self._audio_recaps = audio_recaps

        self.create = async_to_streamed_response_wrapper(
            audio_recaps.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            audio_recaps.retrieve,
        )
        self.ask_question = async_to_streamed_response_wrapper(
            audio_recaps.ask_question,
        )

    @cached_property
    def sections(self) -> AsyncSectionsResourceWithStreamingResponse:
        return AsyncSectionsResourceWithStreamingResponse(self._audio_recaps.sections)
