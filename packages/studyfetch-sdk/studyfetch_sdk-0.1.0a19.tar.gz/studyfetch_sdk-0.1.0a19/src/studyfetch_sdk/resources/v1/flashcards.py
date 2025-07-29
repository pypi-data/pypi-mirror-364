# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v1 import (
    flashcard_rate_params,
    flashcard_get_all_params,
    flashcard_get_due_params,
    flashcard_get_stats_params,
    flashcard_batch_process_params,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v1.flashcard_get_types_response import FlashcardGetTypesResponse
from ...types.v1.flashcard_batch_process_response import FlashcardBatchProcessResponse
from ...types.v1.flashcard_get_algorithm_response import FlashcardGetAlgorithmResponse

__all__ = ["FlashcardsResource", "AsyncFlashcardsResource"]


class FlashcardsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FlashcardsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return FlashcardsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FlashcardsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return FlashcardsResourceWithStreamingResponse(self)

    def batch_process(
        self,
        component_id: str,
        *,
        operations: Iterable[flashcard_batch_process_params.Operation],
        group_id: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlashcardBatchProcessResponse:
        """
        Process multiple flashcard operations

        Args:
          group_id: Group ID (optional)

          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        return self._post(
            f"/api/v1/flashcards/{component_id}/batch",
            body=maybe_transform(
                {
                    "operations": operations,
                    "group_id": group_id,
                    "user_id": user_id,
                },
                flashcard_batch_process_params.FlashcardBatchProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FlashcardBatchProcessResponse,
        )

    def get_algorithm(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlashcardGetAlgorithmResponse:
        """Get spaced repetition algorithm info"""
        return self._get(
            "/api/v1/flashcards/algorithm",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FlashcardGetAlgorithmResponse,
        )

    def get_all(
        self,
        component_id: str,
        *,
        group_ids: str | NotGiven = NOT_GIVEN,
        limit: float | NotGiven = NOT_GIVEN,
        offset: float | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get all flashcards for component

        Args:
          group_ids: Group IDs (comma-separated)

          limit: Max number of cards

          offset: Offset

          user_id: User ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/flashcards/{component_id}/all",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "group_ids": group_ids,
                        "limit": limit,
                        "offset": offset,
                        "user_id": user_id,
                    },
                    flashcard_get_all_params.FlashcardGetAllParams,
                ),
            ),
            cast_to=NoneType,
        )

    def get_due(
        self,
        component_id: str,
        *,
        group_ids: str,
        limit: float | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get due flashcards for review

        Args:
          limit: Max number of cards

          user_id: User ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/flashcards/{component_id}/due",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "group_ids": group_ids,
                        "limit": limit,
                        "user_id": user_id,
                    },
                    flashcard_get_due_params.FlashcardGetDueParams,
                ),
            ),
            cast_to=NoneType,
        )

    def get_stats(
        self,
        component_id: str,
        *,
        group_ids: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get flashcard statistics

        Args:
          group_ids: Group IDs (comma-separated)

          user_id: User ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/flashcards/{component_id}/stats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "group_ids": group_ids,
                        "user_id": user_id,
                    },
                    flashcard_get_stats_params.FlashcardGetStatsParams,
                ),
            ),
            cast_to=NoneType,
        )

    def get_types(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlashcardGetTypesResponse:
        """Get available flashcard types"""
        return self._get(
            "/api/v1/flashcards/types",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FlashcardGetTypesResponse,
        )

    def rate(
        self,
        component_id: str,
        *,
        card_id: str,
        rating: float,
        group_id: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Rate a flashcard

        Args:
          card_id: Flashcard ID

          rating: Rating (0-3)

          group_id: Group ID (optional)

          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/flashcards/{component_id}/rate",
            body=maybe_transform(
                {
                    "card_id": card_id,
                    "rating": rating,
                    "group_id": group_id,
                    "user_id": user_id,
                },
                flashcard_rate_params.FlashcardRateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncFlashcardsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFlashcardsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFlashcardsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFlashcardsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncFlashcardsResourceWithStreamingResponse(self)

    async def batch_process(
        self,
        component_id: str,
        *,
        operations: Iterable[flashcard_batch_process_params.Operation],
        group_id: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlashcardBatchProcessResponse:
        """
        Process multiple flashcard operations

        Args:
          group_id: Group ID (optional)

          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        return await self._post(
            f"/api/v1/flashcards/{component_id}/batch",
            body=await async_maybe_transform(
                {
                    "operations": operations,
                    "group_id": group_id,
                    "user_id": user_id,
                },
                flashcard_batch_process_params.FlashcardBatchProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FlashcardBatchProcessResponse,
        )

    async def get_algorithm(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlashcardGetAlgorithmResponse:
        """Get spaced repetition algorithm info"""
        return await self._get(
            "/api/v1/flashcards/algorithm",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FlashcardGetAlgorithmResponse,
        )

    async def get_all(
        self,
        component_id: str,
        *,
        group_ids: str | NotGiven = NOT_GIVEN,
        limit: float | NotGiven = NOT_GIVEN,
        offset: float | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get all flashcards for component

        Args:
          group_ids: Group IDs (comma-separated)

          limit: Max number of cards

          offset: Offset

          user_id: User ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/flashcards/{component_id}/all",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "group_ids": group_ids,
                        "limit": limit,
                        "offset": offset,
                        "user_id": user_id,
                    },
                    flashcard_get_all_params.FlashcardGetAllParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def get_due(
        self,
        component_id: str,
        *,
        group_ids: str,
        limit: float | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get due flashcards for review

        Args:
          limit: Max number of cards

          user_id: User ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/flashcards/{component_id}/due",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "group_ids": group_ids,
                        "limit": limit,
                        "user_id": user_id,
                    },
                    flashcard_get_due_params.FlashcardGetDueParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def get_stats(
        self,
        component_id: str,
        *,
        group_ids: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get flashcard statistics

        Args:
          group_ids: Group IDs (comma-separated)

          user_id: User ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/flashcards/{component_id}/stats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "group_ids": group_ids,
                        "user_id": user_id,
                    },
                    flashcard_get_stats_params.FlashcardGetStatsParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def get_types(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlashcardGetTypesResponse:
        """Get available flashcard types"""
        return await self._get(
            "/api/v1/flashcards/types",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FlashcardGetTypesResponse,
        )

    async def rate(
        self,
        component_id: str,
        *,
        card_id: str,
        rating: float,
        group_id: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Rate a flashcard

        Args:
          card_id: Flashcard ID

          rating: Rating (0-3)

          group_id: Group ID (optional)

          user_id: User ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/flashcards/{component_id}/rate",
            body=await async_maybe_transform(
                {
                    "card_id": card_id,
                    "rating": rating,
                    "group_id": group_id,
                    "user_id": user_id,
                },
                flashcard_rate_params.FlashcardRateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class FlashcardsResourceWithRawResponse:
    def __init__(self, flashcards: FlashcardsResource) -> None:
        self._flashcards = flashcards

        self.batch_process = to_raw_response_wrapper(
            flashcards.batch_process,
        )
        self.get_algorithm = to_raw_response_wrapper(
            flashcards.get_algorithm,
        )
        self.get_all = to_raw_response_wrapper(
            flashcards.get_all,
        )
        self.get_due = to_raw_response_wrapper(
            flashcards.get_due,
        )
        self.get_stats = to_raw_response_wrapper(
            flashcards.get_stats,
        )
        self.get_types = to_raw_response_wrapper(
            flashcards.get_types,
        )
        self.rate = to_raw_response_wrapper(
            flashcards.rate,
        )


class AsyncFlashcardsResourceWithRawResponse:
    def __init__(self, flashcards: AsyncFlashcardsResource) -> None:
        self._flashcards = flashcards

        self.batch_process = async_to_raw_response_wrapper(
            flashcards.batch_process,
        )
        self.get_algorithm = async_to_raw_response_wrapper(
            flashcards.get_algorithm,
        )
        self.get_all = async_to_raw_response_wrapper(
            flashcards.get_all,
        )
        self.get_due = async_to_raw_response_wrapper(
            flashcards.get_due,
        )
        self.get_stats = async_to_raw_response_wrapper(
            flashcards.get_stats,
        )
        self.get_types = async_to_raw_response_wrapper(
            flashcards.get_types,
        )
        self.rate = async_to_raw_response_wrapper(
            flashcards.rate,
        )


class FlashcardsResourceWithStreamingResponse:
    def __init__(self, flashcards: FlashcardsResource) -> None:
        self._flashcards = flashcards

        self.batch_process = to_streamed_response_wrapper(
            flashcards.batch_process,
        )
        self.get_algorithm = to_streamed_response_wrapper(
            flashcards.get_algorithm,
        )
        self.get_all = to_streamed_response_wrapper(
            flashcards.get_all,
        )
        self.get_due = to_streamed_response_wrapper(
            flashcards.get_due,
        )
        self.get_stats = to_streamed_response_wrapper(
            flashcards.get_stats,
        )
        self.get_types = to_streamed_response_wrapper(
            flashcards.get_types,
        )
        self.rate = to_streamed_response_wrapper(
            flashcards.rate,
        )


class AsyncFlashcardsResourceWithStreamingResponse:
    def __init__(self, flashcards: AsyncFlashcardsResource) -> None:
        self._flashcards = flashcards

        self.batch_process = async_to_streamed_response_wrapper(
            flashcards.batch_process,
        )
        self.get_algorithm = async_to_streamed_response_wrapper(
            flashcards.get_algorithm,
        )
        self.get_all = async_to_streamed_response_wrapper(
            flashcards.get_all,
        )
        self.get_due = async_to_streamed_response_wrapper(
            flashcards.get_due,
        )
        self.get_stats = async_to_streamed_response_wrapper(
            flashcards.get_stats,
        )
        self.get_types = async_to_streamed_response_wrapper(
            flashcards.get_types,
        )
        self.rate = async_to_streamed_response_wrapper(
            flashcards.rate,
        )
