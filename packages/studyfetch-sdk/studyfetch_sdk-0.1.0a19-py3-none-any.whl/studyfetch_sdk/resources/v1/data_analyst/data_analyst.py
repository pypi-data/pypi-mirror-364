# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable

import httpx

from .test import (
    TestResource,
    AsyncTestResource,
    TestResourceWithRawResponse,
    AsyncTestResourceWithRawResponse,
    TestResourceWithStreamingResponse,
    AsyncTestResourceWithStreamingResponse,
)
from .sessions import (
    SessionsResource,
    AsyncSessionsResource,
    SessionsResourceWithRawResponse,
    AsyncSessionsResourceWithRawResponse,
    SessionsResourceWithStreamingResponse,
    AsyncSessionsResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import maybe_transform, strip_not_given, async_maybe_transform
from ...._compat import cached_property
from ....types.v1 import (
    data_analyst_stream_params,
    data_analyst_send_message_params,
    data_analyst_retrieve_session_params,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options

__all__ = ["DataAnalystResource", "AsyncDataAnalystResource"]


class DataAnalystResource(SyncAPIResource):
    @cached_property
    def sessions(self) -> SessionsResource:
        return SessionsResource(self._client)

    @cached_property
    def test(self) -> TestResource:
        return TestResource(self._client)

    @cached_property
    def with_raw_response(self) -> DataAnalystResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return DataAnalystResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DataAnalystResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return DataAnalystResourceWithStreamingResponse(self)

    def get_history(
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
            "/api/v1/data-analyst/history",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_session(
        self,
        session_id: str,
        *,
        user_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/data-analyst/session/{session_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"user_id": user_id}, data_analyst_retrieve_session_params.DataAnalystRetrieveSessionParams
                ),
            ),
            cast_to=NoneType,
        )

    def send_followups(
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
            "/api/v1/data-analyst/followups",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def send_message(
        self,
        *,
        component_id: str,
        message: data_analyst_send_message_params.Message,
        x_component_id: str,
        context: object | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        session_id: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Args:
          component_id: Component ID for context

          message: Chat message content

          context: Additional context data

          group_ids: Group IDs for collaboration

          session_id: Session ID for conversation continuity

          user_id: User ID for tracking

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers.update({"x-component-id": x_component_id})
        return self._post(
            "/api/v1/data-analyst/message",
            body=maybe_transform(
                {
                    "component_id": component_id,
                    "message": message,
                    "context": context,
                    "group_ids": group_ids,
                    "session_id": session_id,
                    "user_id": user_id,
                },
                data_analyst_send_message_params.DataAnalystSendMessageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def stream(
        self,
        *,
        context: object | NotGiven = NOT_GIVEN,
        group_id: str | NotGiven = NOT_GIVEN,
        messages: Iterable[data_analyst_stream_params.Message] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        x_component_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Stream chat responses

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"x-component-id": x_component_id}), **(extra_headers or {})}
        return self._post(
            "/api/v1/data-analyst/stream",
            body=maybe_transform(
                {
                    "context": context,
                    "group_id": group_id,
                    "messages": messages,
                    "user_id": user_id,
                },
                data_analyst_stream_params.DataAnalystStreamParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncDataAnalystResource(AsyncAPIResource):
    @cached_property
    def sessions(self) -> AsyncSessionsResource:
        return AsyncSessionsResource(self._client)

    @cached_property
    def test(self) -> AsyncTestResource:
        return AsyncTestResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDataAnalystResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDataAnalystResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDataAnalystResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncDataAnalystResourceWithStreamingResponse(self)

    async def get_history(
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
            "/api/v1/data-analyst/history",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_session(
        self,
        session_id: str,
        *,
        user_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/data-analyst/session/{session_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"user_id": user_id}, data_analyst_retrieve_session_params.DataAnalystRetrieveSessionParams
                ),
            ),
            cast_to=NoneType,
        )

    async def send_followups(
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
            "/api/v1/data-analyst/followups",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def send_message(
        self,
        *,
        component_id: str,
        message: data_analyst_send_message_params.Message,
        x_component_id: str,
        context: object | NotGiven = NOT_GIVEN,
        group_ids: List[str] | NotGiven = NOT_GIVEN,
        session_id: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Args:
          component_id: Component ID for context

          message: Chat message content

          context: Additional context data

          group_ids: Group IDs for collaboration

          session_id: Session ID for conversation continuity

          user_id: User ID for tracking

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers.update({"x-component-id": x_component_id})
        return await self._post(
            "/api/v1/data-analyst/message",
            body=await async_maybe_transform(
                {
                    "component_id": component_id,
                    "message": message,
                    "context": context,
                    "group_ids": group_ids,
                    "session_id": session_id,
                    "user_id": user_id,
                },
                data_analyst_send_message_params.DataAnalystSendMessageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def stream(
        self,
        *,
        context: object | NotGiven = NOT_GIVEN,
        group_id: str | NotGiven = NOT_GIVEN,
        messages: Iterable[data_analyst_stream_params.Message] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        x_component_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Stream chat responses

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"x-component-id": x_component_id}), **(extra_headers or {})}
        return await self._post(
            "/api/v1/data-analyst/stream",
            body=await async_maybe_transform(
                {
                    "context": context,
                    "group_id": group_id,
                    "messages": messages,
                    "user_id": user_id,
                },
                data_analyst_stream_params.DataAnalystStreamParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class DataAnalystResourceWithRawResponse:
    def __init__(self, data_analyst: DataAnalystResource) -> None:
        self._data_analyst = data_analyst

        self.get_history = to_raw_response_wrapper(
            data_analyst.get_history,
        )
        self.retrieve_session = to_raw_response_wrapper(
            data_analyst.retrieve_session,
        )
        self.send_followups = to_raw_response_wrapper(
            data_analyst.send_followups,
        )
        self.send_message = to_raw_response_wrapper(
            data_analyst.send_message,
        )
        self.stream = to_raw_response_wrapper(
            data_analyst.stream,
        )

    @cached_property
    def sessions(self) -> SessionsResourceWithRawResponse:
        return SessionsResourceWithRawResponse(self._data_analyst.sessions)

    @cached_property
    def test(self) -> TestResourceWithRawResponse:
        return TestResourceWithRawResponse(self._data_analyst.test)


class AsyncDataAnalystResourceWithRawResponse:
    def __init__(self, data_analyst: AsyncDataAnalystResource) -> None:
        self._data_analyst = data_analyst

        self.get_history = async_to_raw_response_wrapper(
            data_analyst.get_history,
        )
        self.retrieve_session = async_to_raw_response_wrapper(
            data_analyst.retrieve_session,
        )
        self.send_followups = async_to_raw_response_wrapper(
            data_analyst.send_followups,
        )
        self.send_message = async_to_raw_response_wrapper(
            data_analyst.send_message,
        )
        self.stream = async_to_raw_response_wrapper(
            data_analyst.stream,
        )

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithRawResponse:
        return AsyncSessionsResourceWithRawResponse(self._data_analyst.sessions)

    @cached_property
    def test(self) -> AsyncTestResourceWithRawResponse:
        return AsyncTestResourceWithRawResponse(self._data_analyst.test)


class DataAnalystResourceWithStreamingResponse:
    def __init__(self, data_analyst: DataAnalystResource) -> None:
        self._data_analyst = data_analyst

        self.get_history = to_streamed_response_wrapper(
            data_analyst.get_history,
        )
        self.retrieve_session = to_streamed_response_wrapper(
            data_analyst.retrieve_session,
        )
        self.send_followups = to_streamed_response_wrapper(
            data_analyst.send_followups,
        )
        self.send_message = to_streamed_response_wrapper(
            data_analyst.send_message,
        )
        self.stream = to_streamed_response_wrapper(
            data_analyst.stream,
        )

    @cached_property
    def sessions(self) -> SessionsResourceWithStreamingResponse:
        return SessionsResourceWithStreamingResponse(self._data_analyst.sessions)

    @cached_property
    def test(self) -> TestResourceWithStreamingResponse:
        return TestResourceWithStreamingResponse(self._data_analyst.test)


class AsyncDataAnalystResourceWithStreamingResponse:
    def __init__(self, data_analyst: AsyncDataAnalystResource) -> None:
        self._data_analyst = data_analyst

        self.get_history = async_to_streamed_response_wrapper(
            data_analyst.get_history,
        )
        self.retrieve_session = async_to_streamed_response_wrapper(
            data_analyst.retrieve_session,
        )
        self.send_followups = async_to_streamed_response_wrapper(
            data_analyst.send_followups,
        )
        self.send_message = async_to_streamed_response_wrapper(
            data_analyst.send_message,
        )
        self.stream = async_to_streamed_response_wrapper(
            data_analyst.stream,
        )

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithStreamingResponse:
        return AsyncSessionsResourceWithStreamingResponse(self._data_analyst.sessions)

    @cached_property
    def test(self) -> AsyncTestResourceWithStreamingResponse:
        return AsyncTestResourceWithStreamingResponse(self._data_analyst.test)
