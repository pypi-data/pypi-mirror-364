# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from .component import (
    ComponentResource,
    AsyncComponentResource,
    ComponentResourceWithRawResponse,
    AsyncComponentResourceWithRawResponse,
    ComponentResourceWithStreamingResponse,
    AsyncComponentResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ....types.v1 import test_create_params, test_retake_params, test_submit_params, test_submit_answer_params
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options

__all__ = ["TestsResource", "AsyncTestsResource"]


class TestsResource(SyncAPIResource):
    __test__ = False

    @cached_property
    def component(self) -> ComponentResource:
        return ComponentResource(self._client)

    @cached_property
    def with_raw_response(self) -> TestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return TestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return TestsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        component_id: str,
        name: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a new test

        Args:
          component_id: Component ID

          name: Test name (optional)

          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/api/v1/tests/create",
            body=maybe_transform(
                {
                    "component_id": component_id,
                    "name": name,
                    "user_id": user_id,
                },
                test_create_params.TestCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve(
        self,
        test_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get test by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not test_id:
            raise ValueError(f"Expected a non-empty value for `test_id` but received {test_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/tests/{test_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_results(
        self,
        test_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get test results

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not test_id:
            raise ValueError(f"Expected a non-empty value for `test_id` but received {test_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/tests/{test_id}/results",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retake(
        self,
        test_id: str,
        *,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Retake a test

        Args:
          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not test_id:
            raise ValueError(f"Expected a non-empty value for `test_id` but received {test_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/tests/{test_id}/retake",
            body=maybe_transform({"user_id": user_id}, test_retake_params.TestRetakeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def submit(
        self,
        test_id: str,
        *,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Submit completed test

        Args:
          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not test_id:
            raise ValueError(f"Expected a non-empty value for `test_id` but received {test_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/tests/{test_id}/submit",
            body=maybe_transform({"user_id": user_id}, test_submit_params.TestSubmitParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def submit_answer(
        self,
        test_id: str,
        *,
        answer: str,
        question_id: str,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Submit test answer

        Args:
          answer: User answer

          question_id: Question ID

          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not test_id:
            raise ValueError(f"Expected a non-empty value for `test_id` but received {test_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/tests/{test_id}/submit-answer",
            body=maybe_transform(
                {
                    "answer": answer,
                    "question_id": question_id,
                    "user_id": user_id,
                },
                test_submit_answer_params.TestSubmitAnswerParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncTestsResource(AsyncAPIResource):
    @cached_property
    def component(self) -> AsyncComponentResource:
        return AsyncComponentResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncTestsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        component_id: str,
        name: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a new test

        Args:
          component_id: Component ID

          name: Test name (optional)

          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/api/v1/tests/create",
            body=await async_maybe_transform(
                {
                    "component_id": component_id,
                    "name": name,
                    "user_id": user_id,
                },
                test_create_params.TestCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve(
        self,
        test_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get test by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not test_id:
            raise ValueError(f"Expected a non-empty value for `test_id` but received {test_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/tests/{test_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_results(
        self,
        test_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get test results

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not test_id:
            raise ValueError(f"Expected a non-empty value for `test_id` but received {test_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/tests/{test_id}/results",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retake(
        self,
        test_id: str,
        *,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Retake a test

        Args:
          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not test_id:
            raise ValueError(f"Expected a non-empty value for `test_id` but received {test_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/tests/{test_id}/retake",
            body=await async_maybe_transform({"user_id": user_id}, test_retake_params.TestRetakeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def submit(
        self,
        test_id: str,
        *,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Submit completed test

        Args:
          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not test_id:
            raise ValueError(f"Expected a non-empty value for `test_id` but received {test_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/tests/{test_id}/submit",
            body=await async_maybe_transform({"user_id": user_id}, test_submit_params.TestSubmitParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def submit_answer(
        self,
        test_id: str,
        *,
        answer: str,
        question_id: str,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Submit test answer

        Args:
          answer: User answer

          question_id: Question ID

          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not test_id:
            raise ValueError(f"Expected a non-empty value for `test_id` but received {test_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/tests/{test_id}/submit-answer",
            body=await async_maybe_transform(
                {
                    "answer": answer,
                    "question_id": question_id,
                    "user_id": user_id,
                },
                test_submit_answer_params.TestSubmitAnswerParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class TestsResourceWithRawResponse:
    __test__ = False

    def __init__(self, tests: TestsResource) -> None:
        self._tests = tests

        self.create = to_raw_response_wrapper(
            tests.create,
        )
        self.retrieve = to_raw_response_wrapper(
            tests.retrieve,
        )
        self.get_results = to_raw_response_wrapper(
            tests.get_results,
        )
        self.retake = to_raw_response_wrapper(
            tests.retake,
        )
        self.submit = to_raw_response_wrapper(
            tests.submit,
        )
        self.submit_answer = to_raw_response_wrapper(
            tests.submit_answer,
        )

    @cached_property
    def component(self) -> ComponentResourceWithRawResponse:
        return ComponentResourceWithRawResponse(self._tests.component)


class AsyncTestsResourceWithRawResponse:
    def __init__(self, tests: AsyncTestsResource) -> None:
        self._tests = tests

        self.create = async_to_raw_response_wrapper(
            tests.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            tests.retrieve,
        )
        self.get_results = async_to_raw_response_wrapper(
            tests.get_results,
        )
        self.retake = async_to_raw_response_wrapper(
            tests.retake,
        )
        self.submit = async_to_raw_response_wrapper(
            tests.submit,
        )
        self.submit_answer = async_to_raw_response_wrapper(
            tests.submit_answer,
        )

    @cached_property
    def component(self) -> AsyncComponentResourceWithRawResponse:
        return AsyncComponentResourceWithRawResponse(self._tests.component)


class TestsResourceWithStreamingResponse:
    __test__ = False

    def __init__(self, tests: TestsResource) -> None:
        self._tests = tests

        self.create = to_streamed_response_wrapper(
            tests.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            tests.retrieve,
        )
        self.get_results = to_streamed_response_wrapper(
            tests.get_results,
        )
        self.retake = to_streamed_response_wrapper(
            tests.retake,
        )
        self.submit = to_streamed_response_wrapper(
            tests.submit,
        )
        self.submit_answer = to_streamed_response_wrapper(
            tests.submit_answer,
        )

    @cached_property
    def component(self) -> ComponentResourceWithStreamingResponse:
        return ComponentResourceWithStreamingResponse(self._tests.component)


class AsyncTestsResourceWithStreamingResponse:
    def __init__(self, tests: AsyncTestsResource) -> None:
        self._tests = tests

        self.create = async_to_streamed_response_wrapper(
            tests.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            tests.retrieve,
        )
        self.get_results = async_to_streamed_response_wrapper(
            tests.get_results,
        )
        self.retake = async_to_streamed_response_wrapper(
            tests.retake,
        )
        self.submit = async_to_streamed_response_wrapper(
            tests.submit,
        )
        self.submit_answer = async_to_streamed_response_wrapper(
            tests.submit_answer,
        )

    @cached_property
    def component(self) -> AsyncComponentResourceWithStreamingResponse:
        return AsyncComponentResourceWithStreamingResponse(self._tests.component)
