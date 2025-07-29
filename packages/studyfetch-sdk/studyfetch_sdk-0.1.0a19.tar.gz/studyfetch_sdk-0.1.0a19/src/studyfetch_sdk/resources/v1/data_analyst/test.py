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

__all__ = ["TestResource", "AsyncTestResource"]


class TestResource(SyncAPIResource):
    __test__ = False

    @cached_property
    def with_raw_response(self) -> TestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return TestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return TestResourceWithStreamingResponse(self)

    def upload_image(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/api/v1/data-analyst/test/image",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def upload_image_citation(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/api/v1/data-analyst/test/image-citation",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncTestResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncTestResourceWithStreamingResponse(self)

    async def upload_image(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/api/v1/data-analyst/test/image",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def upload_image_citation(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/api/v1/data-analyst/test/image-citation",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class TestResourceWithRawResponse:
    __test__ = False

    def __init__(self, test: TestResource) -> None:
        self._test = test

        self.upload_image = to_raw_response_wrapper(
            test.upload_image,
        )
        self.upload_image_citation = to_raw_response_wrapper(
            test.upload_image_citation,
        )


class AsyncTestResourceWithRawResponse:
    def __init__(self, test: AsyncTestResource) -> None:
        self._test = test

        self.upload_image = async_to_raw_response_wrapper(
            test.upload_image,
        )
        self.upload_image_citation = async_to_raw_response_wrapper(
            test.upload_image_citation,
        )


class TestResourceWithStreamingResponse:
    __test__ = False

    def __init__(self, test: TestResource) -> None:
        self._test = test

        self.upload_image = to_streamed_response_wrapper(
            test.upload_image,
        )
        self.upload_image_citation = to_streamed_response_wrapper(
            test.upload_image_citation,
        )


class AsyncTestResourceWithStreamingResponse:
    def __init__(self, test: AsyncTestResource) -> None:
        self._test = test

        self.upload_image = async_to_streamed_response_wrapper(
            test.upload_image,
        )
        self.upload_image_citation = async_to_streamed_response_wrapper(
            test.upload_image_citation,
        )
