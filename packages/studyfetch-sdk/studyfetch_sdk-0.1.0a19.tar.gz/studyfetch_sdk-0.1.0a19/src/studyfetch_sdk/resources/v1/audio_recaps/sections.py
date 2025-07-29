# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

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

__all__ = ["SectionsResource", "AsyncSectionsResource"]


class SectionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SectionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SectionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SectionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return SectionsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        section_id: str,
        *,
        recap_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get specific audio recap section

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not recap_id:
            raise ValueError(f"Expected a non-empty value for `recap_id` but received {recap_id!r}")
        if not section_id:
            raise ValueError(f"Expected a non-empty value for `section_id` but received {section_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/audio-recaps/{recap_id}/sections/{section_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def list(
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
        Get audio recap sections

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
            f"/api/v1/audio-recaps/{recap_id}/sections",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncSectionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSectionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSectionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSectionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncSectionsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        section_id: str,
        *,
        recap_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get specific audio recap section

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not recap_id:
            raise ValueError(f"Expected a non-empty value for `recap_id` but received {recap_id!r}")
        if not section_id:
            raise ValueError(f"Expected a non-empty value for `section_id` but received {section_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/audio-recaps/{recap_id}/sections/{section_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def list(
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
        Get audio recap sections

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
            f"/api/v1/audio-recaps/{recap_id}/sections",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class SectionsResourceWithRawResponse:
    def __init__(self, sections: SectionsResource) -> None:
        self._sections = sections

        self.retrieve = to_raw_response_wrapper(
            sections.retrieve,
        )
        self.list = to_raw_response_wrapper(
            sections.list,
        )


class AsyncSectionsResourceWithRawResponse:
    def __init__(self, sections: AsyncSectionsResource) -> None:
        self._sections = sections

        self.retrieve = async_to_raw_response_wrapper(
            sections.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            sections.list,
        )


class SectionsResourceWithStreamingResponse:
    def __init__(self, sections: SectionsResource) -> None:
        self._sections = sections

        self.retrieve = to_streamed_response_wrapper(
            sections.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            sections.list,
        )


class AsyncSectionsResourceWithStreamingResponse:
    def __init__(self, sections: AsyncSectionsResource) -> None:
        self._sections = sections

        self.retrieve = async_to_streamed_response_wrapper(
            sections.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            sections.list,
        )
