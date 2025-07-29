# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from .sessions import (
    SessionsResource,
    AsyncSessionsResource,
    SessionsResourceWithRawResponse,
    AsyncSessionsResourceWithRawResponse,
    SessionsResourceWithStreamingResponse,
    AsyncSessionsResourceWithStreamingResponse,
)
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
from ....types.v1 import scenario_create_params, scenario_update_params, scenario_submit_answer_params
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from .submissions.submissions import (
    SubmissionsResource,
    AsyncSubmissionsResource,
    SubmissionsResourceWithRawResponse,
    AsyncSubmissionsResourceWithRawResponse,
    SubmissionsResourceWithStreamingResponse,
    AsyncSubmissionsResourceWithStreamingResponse,
)

__all__ = ["ScenariosResource", "AsyncScenariosResource"]


class ScenariosResource(SyncAPIResource):
    @cached_property
    def component(self) -> ComponentResource:
        return ComponentResource(self._client)

    @cached_property
    def sessions(self) -> SessionsResource:
        return SessionsResource(self._client)

    @cached_property
    def submissions(self) -> SubmissionsResource:
        return SubmissionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ScenariosResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ScenariosResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ScenariosResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return ScenariosResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        component_id: str,
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
        Create a new scenario

        Args:
          component_id: Associated component ID

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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/api/v1/scenarios",
            body=maybe_transform(
                {
                    "component_id": component_id,
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
                scenario_create_params.ScenarioCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get scenario by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/scenarios/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def update(
        self,
        id: str,
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
        Update scenario

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._put(
            f"/api/v1/scenarios/{id}",
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
                scenario_update_params.ScenarioUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Get all scenarios"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/api/v1/scenarios",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete scenario

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/v1/scenarios/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_stats(
        self,
        id: str,
        *,
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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v1/scenarios/{id}/stats",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def submit_answer(
        self,
        id: str,
        *,
        conversation_history: Iterable[object],
        final_answer: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Submit scenario answer

        Args:
          conversation_history: Conversation history

          final_answer: Final answer for the scenario

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/scenarios/{id}/submit",
            body=maybe_transform(
                {
                    "conversation_history": conversation_history,
                    "final_answer": final_answer,
                },
                scenario_submit_answer_params.ScenarioSubmitAnswerParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncScenariosResource(AsyncAPIResource):
    @cached_property
    def component(self) -> AsyncComponentResource:
        return AsyncComponentResource(self._client)

    @cached_property
    def sessions(self) -> AsyncSessionsResource:
        return AsyncSessionsResource(self._client)

    @cached_property
    def submissions(self) -> AsyncSubmissionsResource:
        return AsyncSubmissionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncScenariosResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncScenariosResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncScenariosResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncScenariosResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        component_id: str,
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
        Create a new scenario

        Args:
          component_id: Associated component ID

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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/api/v1/scenarios",
            body=await async_maybe_transform(
                {
                    "component_id": component_id,
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
                scenario_create_params.ScenarioCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Get scenario by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/scenarios/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def update(
        self,
        id: str,
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
        Update scenario

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._put(
            f"/api/v1/scenarios/{id}",
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
                scenario_update_params.ScenarioUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Get all scenarios"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/api/v1/scenarios",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete scenario

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/v1/scenarios/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_stats(
        self,
        id: str,
        *,
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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v1/scenarios/{id}/stats",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def submit_answer(
        self,
        id: str,
        *,
        conversation_history: Iterable[object],
        final_answer: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Submit scenario answer

        Args:
          conversation_history: Conversation history

          final_answer: Final answer for the scenario

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/scenarios/{id}/submit",
            body=await async_maybe_transform(
                {
                    "conversation_history": conversation_history,
                    "final_answer": final_answer,
                },
                scenario_submit_answer_params.ScenarioSubmitAnswerParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ScenariosResourceWithRawResponse:
    def __init__(self, scenarios: ScenariosResource) -> None:
        self._scenarios = scenarios

        self.create = to_raw_response_wrapper(
            scenarios.create,
        )
        self.retrieve = to_raw_response_wrapper(
            scenarios.retrieve,
        )
        self.update = to_raw_response_wrapper(
            scenarios.update,
        )
        self.list = to_raw_response_wrapper(
            scenarios.list,
        )
        self.delete = to_raw_response_wrapper(
            scenarios.delete,
        )
        self.get_stats = to_raw_response_wrapper(
            scenarios.get_stats,
        )
        self.submit_answer = to_raw_response_wrapper(
            scenarios.submit_answer,
        )

    @cached_property
    def component(self) -> ComponentResourceWithRawResponse:
        return ComponentResourceWithRawResponse(self._scenarios.component)

    @cached_property
    def sessions(self) -> SessionsResourceWithRawResponse:
        return SessionsResourceWithRawResponse(self._scenarios.sessions)

    @cached_property
    def submissions(self) -> SubmissionsResourceWithRawResponse:
        return SubmissionsResourceWithRawResponse(self._scenarios.submissions)


class AsyncScenariosResourceWithRawResponse:
    def __init__(self, scenarios: AsyncScenariosResource) -> None:
        self._scenarios = scenarios

        self.create = async_to_raw_response_wrapper(
            scenarios.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            scenarios.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            scenarios.update,
        )
        self.list = async_to_raw_response_wrapper(
            scenarios.list,
        )
        self.delete = async_to_raw_response_wrapper(
            scenarios.delete,
        )
        self.get_stats = async_to_raw_response_wrapper(
            scenarios.get_stats,
        )
        self.submit_answer = async_to_raw_response_wrapper(
            scenarios.submit_answer,
        )

    @cached_property
    def component(self) -> AsyncComponentResourceWithRawResponse:
        return AsyncComponentResourceWithRawResponse(self._scenarios.component)

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithRawResponse:
        return AsyncSessionsResourceWithRawResponse(self._scenarios.sessions)

    @cached_property
    def submissions(self) -> AsyncSubmissionsResourceWithRawResponse:
        return AsyncSubmissionsResourceWithRawResponse(self._scenarios.submissions)


class ScenariosResourceWithStreamingResponse:
    def __init__(self, scenarios: ScenariosResource) -> None:
        self._scenarios = scenarios

        self.create = to_streamed_response_wrapper(
            scenarios.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            scenarios.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            scenarios.update,
        )
        self.list = to_streamed_response_wrapper(
            scenarios.list,
        )
        self.delete = to_streamed_response_wrapper(
            scenarios.delete,
        )
        self.get_stats = to_streamed_response_wrapper(
            scenarios.get_stats,
        )
        self.submit_answer = to_streamed_response_wrapper(
            scenarios.submit_answer,
        )

    @cached_property
    def component(self) -> ComponentResourceWithStreamingResponse:
        return ComponentResourceWithStreamingResponse(self._scenarios.component)

    @cached_property
    def sessions(self) -> SessionsResourceWithStreamingResponse:
        return SessionsResourceWithStreamingResponse(self._scenarios.sessions)

    @cached_property
    def submissions(self) -> SubmissionsResourceWithStreamingResponse:
        return SubmissionsResourceWithStreamingResponse(self._scenarios.submissions)


class AsyncScenariosResourceWithStreamingResponse:
    def __init__(self, scenarios: AsyncScenariosResource) -> None:
        self._scenarios = scenarios

        self.create = async_to_streamed_response_wrapper(
            scenarios.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            scenarios.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            scenarios.update,
        )
        self.list = async_to_streamed_response_wrapper(
            scenarios.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            scenarios.delete,
        )
        self.get_stats = async_to_streamed_response_wrapper(
            scenarios.get_stats,
        )
        self.submit_answer = async_to_streamed_response_wrapper(
            scenarios.submit_answer,
        )

    @cached_property
    def component(self) -> AsyncComponentResourceWithStreamingResponse:
        return AsyncComponentResourceWithStreamingResponse(self._scenarios.component)

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithStreamingResponse:
        return AsyncSessionsResourceWithStreamingResponse(self._scenarios.sessions)

    @cached_property
    def submissions(self) -> AsyncSubmissionsResourceWithStreamingResponse:
        return AsyncSubmissionsResourceWithStreamingResponse(self._scenarios.submissions)
