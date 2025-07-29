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

    def list(
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/api/v1/tests/component/{component_id}/list",
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

    async def list(
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/tests/component/{component_id}/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ComponentResourceWithRawResponse:
    def __init__(self, component: ComponentResource) -> None:
        self._component = component

        self.list = to_raw_response_wrapper(
            component.list,
        )


class AsyncComponentResourceWithRawResponse:
    def __init__(self, component: AsyncComponentResource) -> None:
        self._component = component

        self.list = async_to_raw_response_wrapper(
            component.list,
        )


class ComponentResourceWithStreamingResponse:
    def __init__(self, component: ComponentResource) -> None:
        self._component = component

        self.list = to_streamed_response_wrapper(
            component.list,
        )


class AsyncComponentResourceWithStreamingResponse:
    def __init__(self, component: AsyncComponentResource) -> None:
        self._component = component

        self.list = async_to_streamed_response_wrapper(
            component.list,
        )
