# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.scenarios import component_update_params

__all__ = ["ComponentResource", "AsyncComponentResource"]


class ComponentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ComponentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ComponentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ComponentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return ComponentResourceWithStreamingResponse(self)

    def retrieve(
        self,
        component_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get scenario by component ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/scenarios/component/{component_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def update(
        self,
        component_id: str,
        *,
        name: str,
        characters: Iterable[object] | NotGiven = NOT_GIVEN,
        context: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        final_answer_prompt: str | NotGiven = NOT_GIVEN,
        format: str | NotGiven = NOT_GIVEN,
        goal: str | NotGiven = NOT_GIVEN,
        greeting_character_id: str | NotGiven = NOT_GIVEN,
        greeting_message: str | NotGiven = NOT_GIVEN,
        requires_final_answer: bool | NotGiven = NOT_GIVEN,
        tools: Iterable[object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Update scenario by component ID

        Args:
          name: Scenario name

          characters: Scenario characters

          context: Scenario context

          description: Scenario description

          final_answer_prompt: Prompt for final answer

          format: Interaction format

          goal: Scenario goal

          greeting_character_id: Character ID for greeting

          greeting_message: Greeting message

          requires_final_answer: Whether scenario requires a final answer

          tools: Available tools

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._put(
            f"/api/v1/scenarios/component/{component_id}",
            body=maybe_transform(
                {
                    "name": name,
                    "characters": characters,
                    "context": context,
                    "description": description,
                    "final_answer_prompt": final_answer_prompt,
                    "format": format,
                    "goal": goal,
                    "greeting_character_id": greeting_character_id,
                    "greeting_message": greeting_message,
                    "requires_final_answer": requires_final_answer,
                    "tools": tools,
                },
                component_update_params.ComponentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def delete(
        self,
        component_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete scenario by component ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/scenarios/component/{component_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncComponentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncComponentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncComponentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncComponentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncComponentResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        component_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get scenario by component ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/scenarios/component/{component_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def update(
        self,
        component_id: str,
        *,
        name: str,
        characters: Iterable[object] | NotGiven = NOT_GIVEN,
        context: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        final_answer_prompt: str | NotGiven = NOT_GIVEN,
        format: str | NotGiven = NOT_GIVEN,
        goal: str | NotGiven = NOT_GIVEN,
        greeting_character_id: str | NotGiven = NOT_GIVEN,
        greeting_message: str | NotGiven = NOT_GIVEN,
        requires_final_answer: bool | NotGiven = NOT_GIVEN,
        tools: Iterable[object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Update scenario by component ID

        Args:
          name: Scenario name

          characters: Scenario characters

          context: Scenario context

          description: Scenario description

          final_answer_prompt: Prompt for final answer

          format: Interaction format

          goal: Scenario goal

          greeting_character_id: Character ID for greeting

          greeting_message: Greeting message

          requires_final_answer: Whether scenario requires a final answer

          tools: Available tools

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._put(
            f"/api/v1/scenarios/component/{component_id}",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "characters": characters,
                    "context": context,
                    "description": description,
                    "final_answer_prompt": final_answer_prompt,
                    "format": format,
                    "goal": goal,
                    "greeting_character_id": greeting_character_id,
                    "greeting_message": greeting_message,
                    "requires_final_answer": requires_final_answer,
                    "tools": tools,
                },
                component_update_params.ComponentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def delete(
        self,
        component_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete scenario by component ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/scenarios/component/{component_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ComponentResourceWithRawResponse:
    def __init__(self, component: ComponentResource) -> None:
        self._component = component

        self.retrieve = to_raw_response_wrapper(
            component.retrieve,
        )
        self.update = to_raw_response_wrapper(
            component.update,
        )
        self.delete = to_raw_response_wrapper(
            component.delete,
        )


class AsyncComponentResourceWithRawResponse:
    def __init__(self, component: AsyncComponentResource) -> None:
        self._component = component

        self.retrieve = async_to_raw_response_wrapper(
            component.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            component.update,
        )
        self.delete = async_to_raw_response_wrapper(
            component.delete,
        )


class ComponentResourceWithStreamingResponse:
    def __init__(self, component: ComponentResource) -> None:
        self._component = component

        self.retrieve = to_streamed_response_wrapper(
            component.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            component.update,
        )
        self.delete = to_streamed_response_wrapper(
            component.delete,
        )


class AsyncComponentResourceWithStreamingResponse:
    def __init__(self, component: AsyncComponentResource) -> None:
        self._component = component

        self.retrieve = async_to_streamed_response_wrapper(
            component.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            component.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            component.delete,
        )
