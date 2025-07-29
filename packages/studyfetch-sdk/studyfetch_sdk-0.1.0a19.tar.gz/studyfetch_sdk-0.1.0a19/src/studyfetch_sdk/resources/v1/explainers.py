# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v1 import explainer_create_params, explainer_handle_webhook_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options

__all__ = ["ExplainersResource", "AsyncExplainersResource"]


class ExplainersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExplainersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ExplainersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExplainersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return ExplainersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        component_id: str,
        folder_ids: List[str],
        material_ids: List[str],
        target_length: float,
        title: str,
        image_search: bool | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        style: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        vertical_video: bool | NotGiven = NOT_GIVEN,
        web_search: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create explainers component

        Args:
          component_id: Component ID

          folder_ids: Folder IDs to include

          material_ids: Material IDs to include

          target_length: Target video length in seconds

          title: Title for the explainer video

          image_search: Enable image search for visuals

          model: AI model to use

          style: Video style

          user_id: User ID

          vertical_video: Create vertical video format (9:16)

          web_search: Enable web search for additional content

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/api/v1/explainers/create",
            body=maybe_transform(
                {
                    "component_id": component_id,
                    "folder_ids": folder_ids,
                    "material_ids": material_ids,
                    "target_length": target_length,
                    "title": title,
                    "image_search": image_search,
                    "model": model,
                    "style": style,
                    "user_id": user_id,
                    "vertical_video": vertical_video,
                    "web_search": web_search,
                },
                explainer_create_params.ExplainerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

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
        Get explainer video by component ID

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
            f"/api/v1/explainers/component/{component_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def handle_webhook(
        self,
        *,
        event: Literal["video.completed", "video.progress", "video.failed"],
        video: explainer_handle_webhook_params.Video,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Handle explainer video webhook events

        Args:
          event: Webhook event type

          video: Video data

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/api/v1/explainers/webhook",
            body=maybe_transform(
                {
                    "event": event,
                    "video": video,
                },
                explainer_handle_webhook_params.ExplainerHandleWebhookParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncExplainersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExplainersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncExplainersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExplainersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncExplainersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        component_id: str,
        folder_ids: List[str],
        material_ids: List[str],
        target_length: float,
        title: str,
        image_search: bool | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        style: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        vertical_video: bool | NotGiven = NOT_GIVEN,
        web_search: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create explainers component

        Args:
          component_id: Component ID

          folder_ids: Folder IDs to include

          material_ids: Material IDs to include

          target_length: Target video length in seconds

          title: Title for the explainer video

          image_search: Enable image search for visuals

          model: AI model to use

          style: Video style

          user_id: User ID

          vertical_video: Create vertical video format (9:16)

          web_search: Enable web search for additional content

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/api/v1/explainers/create",
            body=await async_maybe_transform(
                {
                    "component_id": component_id,
                    "folder_ids": folder_ids,
                    "material_ids": material_ids,
                    "target_length": target_length,
                    "title": title,
                    "image_search": image_search,
                    "model": model,
                    "style": style,
                    "user_id": user_id,
                    "vertical_video": vertical_video,
                    "web_search": web_search,
                },
                explainer_create_params.ExplainerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

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
        Get explainer video by component ID

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
            f"/api/v1/explainers/component/{component_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def handle_webhook(
        self,
        *,
        event: Literal["video.completed", "video.progress", "video.failed"],
        video: explainer_handle_webhook_params.Video,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Handle explainer video webhook events

        Args:
          event: Webhook event type

          video: Video data

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/api/v1/explainers/webhook",
            body=await async_maybe_transform(
                {
                    "event": event,
                    "video": video,
                },
                explainer_handle_webhook_params.ExplainerHandleWebhookParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ExplainersResourceWithRawResponse:
    def __init__(self, explainers: ExplainersResource) -> None:
        self._explainers = explainers

        self.create = to_raw_response_wrapper(
            explainers.create,
        )
        self.retrieve = to_raw_response_wrapper(
            explainers.retrieve,
        )
        self.handle_webhook = to_raw_response_wrapper(
            explainers.handle_webhook,
        )


class AsyncExplainersResourceWithRawResponse:
    def __init__(self, explainers: AsyncExplainersResource) -> None:
        self._explainers = explainers

        self.create = async_to_raw_response_wrapper(
            explainers.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            explainers.retrieve,
        )
        self.handle_webhook = async_to_raw_response_wrapper(
            explainers.handle_webhook,
        )


class ExplainersResourceWithStreamingResponse:
    def __init__(self, explainers: ExplainersResource) -> None:
        self._explainers = explainers

        self.create = to_streamed_response_wrapper(
            explainers.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            explainers.retrieve,
        )
        self.handle_webhook = to_streamed_response_wrapper(
            explainers.handle_webhook,
        )


class AsyncExplainersResourceWithStreamingResponse:
    def __init__(self, explainers: AsyncExplainersResource) -> None:
        self._explainers = explainers

        self.create = async_to_streamed_response_wrapper(
            explainers.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            explainers.retrieve,
        )
        self.handle_webhook = async_to_streamed_response_wrapper(
            explainers.handle_webhook,
        )
