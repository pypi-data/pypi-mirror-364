# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ...._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.upload import (
    component_upload_url_params,
    component_upload_file_params,
    component_complete_upload_params,
    component_get_presigned_url_params,
)
from ....types.v1.upload.file_upload_response import FileUploadResponse
from ....types.v1.upload.component_complete_upload_response import ComponentCompleteUploadResponse
from ....types.v1.upload.component_get_presigned_url_response import ComponentGetPresignedURLResponse

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

    def complete_upload(
        self,
        component_id: str,
        *,
        material_id: str,
        organization_id: str,
        s3_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentCompleteUploadResponse:
        """
        Complete a file upload after using presigned URL

        Args:
          material_id: The ID of the material that was uploaded

          organization_id: The ID of the organization

          s3_key: The S3 key of the uploaded file

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        return self._post(
            f"/api/v1/upload/component/{component_id}/complete",
            body=maybe_transform(
                {
                    "material_id": material_id,
                    "organization_id": organization_id,
                    "s3_key": s3_key,
                },
                component_complete_upload_params.ComponentCompleteUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentCompleteUploadResponse,
        )

    def get_presigned_url(
        self,
        component_id: str,
        *,
        content_type: str,
        filename: str,
        folder_id: str,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentGetPresignedURLResponse:
        """
        Get a presigned URL for direct file upload

        Args:
          content_type: The MIME type of the file

          filename: The name of the file to upload

          folder_id: The ID of the folder to upload to

          organization_id: The ID of the organization

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        return self._post(
            f"/api/v1/upload/component/{component_id}/presigned-url",
            body=maybe_transform(
                {
                    "content_type": content_type,
                    "filename": filename,
                    "folder_id": folder_id,
                    "organization_id": organization_id,
                },
                component_get_presigned_url_params.ComponentGetPresignedURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentGetPresignedURLResponse,
        )

    def upload_file(
        self,
        component_id: str,
        *,
        file: FileTypes,
        folder_id: str,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileUploadResponse:
        """
        Upload a file to a component

        Args:
          file: The file to upload

          folder_id: The ID of the folder to upload to

          organization_id: The ID of the organization

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        body = deepcopy_minimal(
            {
                "file": file,
                "folder_id": folder_id,
                "organization_id": organization_id,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            f"/api/v1/upload/component/{component_id}/file",
            body=maybe_transform(body, component_upload_file_params.ComponentUploadFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileUploadResponse,
        )

    def upload_url(
        self,
        component_id: str,
        *,
        folder_id: str,
        name: str,
        organization_id: str,
        url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileUploadResponse:
        """
        Upload a file from URL to a component

        Args:
          folder_id: The ID of the folder to upload to

          name: The name for the uploaded file

          organization_id: The ID of the organization

          url: The URL of the file to upload

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        return self._post(
            f"/api/v1/upload/component/{component_id}/url",
            body=maybe_transform(
                {
                    "folder_id": folder_id,
                    "name": name,
                    "organization_id": organization_id,
                    "url": url,
                },
                component_upload_url_params.ComponentUploadURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileUploadResponse,
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

    async def complete_upload(
        self,
        component_id: str,
        *,
        material_id: str,
        organization_id: str,
        s3_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentCompleteUploadResponse:
        """
        Complete a file upload after using presigned URL

        Args:
          material_id: The ID of the material that was uploaded

          organization_id: The ID of the organization

          s3_key: The S3 key of the uploaded file

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        return await self._post(
            f"/api/v1/upload/component/{component_id}/complete",
            body=await async_maybe_transform(
                {
                    "material_id": material_id,
                    "organization_id": organization_id,
                    "s3_key": s3_key,
                },
                component_complete_upload_params.ComponentCompleteUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentCompleteUploadResponse,
        )

    async def get_presigned_url(
        self,
        component_id: str,
        *,
        content_type: str,
        filename: str,
        folder_id: str,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ComponentGetPresignedURLResponse:
        """
        Get a presigned URL for direct file upload

        Args:
          content_type: The MIME type of the file

          filename: The name of the file to upload

          folder_id: The ID of the folder to upload to

          organization_id: The ID of the organization

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        return await self._post(
            f"/api/v1/upload/component/{component_id}/presigned-url",
            body=await async_maybe_transform(
                {
                    "content_type": content_type,
                    "filename": filename,
                    "folder_id": folder_id,
                    "organization_id": organization_id,
                },
                component_get_presigned_url_params.ComponentGetPresignedURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComponentGetPresignedURLResponse,
        )

    async def upload_file(
        self,
        component_id: str,
        *,
        file: FileTypes,
        folder_id: str,
        organization_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileUploadResponse:
        """
        Upload a file to a component

        Args:
          file: The file to upload

          folder_id: The ID of the folder to upload to

          organization_id: The ID of the organization

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        body = deepcopy_minimal(
            {
                "file": file,
                "folder_id": folder_id,
                "organization_id": organization_id,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            f"/api/v1/upload/component/{component_id}/file",
            body=await async_maybe_transform(body, component_upload_file_params.ComponentUploadFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileUploadResponse,
        )

    async def upload_url(
        self,
        component_id: str,
        *,
        folder_id: str,
        name: str,
        organization_id: str,
        url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileUploadResponse:
        """
        Upload a file from URL to a component

        Args:
          folder_id: The ID of the folder to upload to

          name: The name for the uploaded file

          organization_id: The ID of the organization

          url: The URL of the file to upload

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not component_id:
            raise ValueError(f"Expected a non-empty value for `component_id` but received {component_id!r}")
        return await self._post(
            f"/api/v1/upload/component/{component_id}/url",
            body=await async_maybe_transform(
                {
                    "folder_id": folder_id,
                    "name": name,
                    "organization_id": organization_id,
                    "url": url,
                },
                component_upload_url_params.ComponentUploadURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileUploadResponse,
        )


class ComponentResourceWithRawResponse:
    def __init__(self, component: ComponentResource) -> None:
        self._component = component

        self.complete_upload = to_raw_response_wrapper(
            component.complete_upload,
        )
        self.get_presigned_url = to_raw_response_wrapper(
            component.get_presigned_url,
        )
        self.upload_file = to_raw_response_wrapper(
            component.upload_file,
        )
        self.upload_url = to_raw_response_wrapper(
            component.upload_url,
        )


class AsyncComponentResourceWithRawResponse:
    def __init__(self, component: AsyncComponentResource) -> None:
        self._component = component

        self.complete_upload = async_to_raw_response_wrapper(
            component.complete_upload,
        )
        self.get_presigned_url = async_to_raw_response_wrapper(
            component.get_presigned_url,
        )
        self.upload_file = async_to_raw_response_wrapper(
            component.upload_file,
        )
        self.upload_url = async_to_raw_response_wrapper(
            component.upload_url,
        )


class ComponentResourceWithStreamingResponse:
    def __init__(self, component: ComponentResource) -> None:
        self._component = component

        self.complete_upload = to_streamed_response_wrapper(
            component.complete_upload,
        )
        self.get_presigned_url = to_streamed_response_wrapper(
            component.get_presigned_url,
        )
        self.upload_file = to_streamed_response_wrapper(
            component.upload_file,
        )
        self.upload_url = to_streamed_response_wrapper(
            component.upload_url,
        )


class AsyncComponentResourceWithStreamingResponse:
    def __init__(self, component: AsyncComponentResource) -> None:
        self._component = component

        self.complete_upload = async_to_streamed_response_wrapper(
            component.complete_upload,
        )
        self.get_presigned_url = async_to_streamed_response_wrapper(
            component.get_presigned_url,
        )
        self.upload_file = async_to_streamed_response_wrapper(
            component.upload_file,
        )
        self.upload_url = async_to_streamed_response_wrapper(
            component.upload_url,
        )
