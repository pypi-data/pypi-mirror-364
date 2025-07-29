# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.materials.test_perform_ocr_response import TestPerformOcrResponse
from ....types.v1.materials.test_process_epub_response import TestProcessEpubResponse
from ....types.v1.materials.test_process_image_response import TestProcessImageResponse
from ....types.v1.materials.test_process_video_response import TestProcessVideoResponse

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

    def perform_ocr(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestPerformOcrResponse:
        """Test OCR functionality with a sample PDF"""
        return self._post(
            "/api/v1/materials/test/ocr",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestPerformOcrResponse,
        )

    def process_epub(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestProcessEpubResponse:
        """Test EPUB processing functionality"""
        return self._post(
            "/api/v1/materials/test/epub-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestProcessEpubResponse,
        )

    def process_image(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestProcessImageResponse:
        """Test image processing with OCR and AI vision"""
        return self._post(
            "/api/v1/materials/test/image-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestProcessImageResponse,
        )

    def process_video(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestProcessVideoResponse:
        """Test video processing setup and dependencies"""
        return self._post(
            "/api/v1/materials/test/video-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestProcessVideoResponse,
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

    async def perform_ocr(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestPerformOcrResponse:
        """Test OCR functionality with a sample PDF"""
        return await self._post(
            "/api/v1/materials/test/ocr",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestPerformOcrResponse,
        )

    async def process_epub(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestProcessEpubResponse:
        """Test EPUB processing functionality"""
        return await self._post(
            "/api/v1/materials/test/epub-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestProcessEpubResponse,
        )

    async def process_image(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestProcessImageResponse:
        """Test image processing with OCR and AI vision"""
        return await self._post(
            "/api/v1/materials/test/image-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestProcessImageResponse,
        )

    async def process_video(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestProcessVideoResponse:
        """Test video processing setup and dependencies"""
        return await self._post(
            "/api/v1/materials/test/video-processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestProcessVideoResponse,
        )


class TestResourceWithRawResponse:
    __test__ = False

    def __init__(self, test: TestResource) -> None:
        self._test = test

        self.perform_ocr = to_raw_response_wrapper(
            test.perform_ocr,
        )
        self.process_epub = to_raw_response_wrapper(
            test.process_epub,
        )
        self.process_image = to_raw_response_wrapper(
            test.process_image,
        )
        self.process_video = to_raw_response_wrapper(
            test.process_video,
        )


class AsyncTestResourceWithRawResponse:
    def __init__(self, test: AsyncTestResource) -> None:
        self._test = test

        self.perform_ocr = async_to_raw_response_wrapper(
            test.perform_ocr,
        )
        self.process_epub = async_to_raw_response_wrapper(
            test.process_epub,
        )
        self.process_image = async_to_raw_response_wrapper(
            test.process_image,
        )
        self.process_video = async_to_raw_response_wrapper(
            test.process_video,
        )


class TestResourceWithStreamingResponse:
    __test__ = False

    def __init__(self, test: TestResource) -> None:
        self._test = test

        self.perform_ocr = to_streamed_response_wrapper(
            test.perform_ocr,
        )
        self.process_epub = to_streamed_response_wrapper(
            test.process_epub,
        )
        self.process_image = to_streamed_response_wrapper(
            test.process_image,
        )
        self.process_video = to_streamed_response_wrapper(
            test.process_video,
        )


class AsyncTestResourceWithStreamingResponse:
    def __init__(self, test: AsyncTestResource) -> None:
        self._test = test

        self.perform_ocr = async_to_streamed_response_wrapper(
            test.perform_ocr,
        )
        self.process_epub = async_to_streamed_response_wrapper(
            test.process_epub,
        )
        self.process_image = async_to_streamed_response_wrapper(
            test.process_image,
        )
        self.process_video = async_to_streamed_response_wrapper(
            test.process_video,
        )
