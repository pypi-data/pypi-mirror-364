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
from ....types.v1.material import Material
from ....types.v1.materials import (
    upload_upload_file_params,
    upload_complete_upload_params,
    upload_upload_from_url_params,
    upload_create_presigned_url_params,
    upload_upload_url_and_process_params,
    upload_upload_file_and_process_params,
)
from ....types.v1.materials.upload_create_presigned_url_response import UploadCreatePresignedURLResponse

__all__ = ["UploadResource", "AsyncUploadResource"]


class UploadResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UploadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return UploadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UploadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return UploadResourceWithStreamingResponse(self)

    def complete_upload(
        self,
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
    ) -> Material:
        """
        Complete upload after using presigned URL

        Args:
          material_id: The ID of the material that was uploaded

          organization_id: The ID of the organization

          s3_key: The S3 key of the uploaded file

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/materials/upload/complete",
            body=maybe_transform(
                {
                    "material_id": material_id,
                    "organization_id": organization_id,
                    "s3_key": s3_key,
                },
                upload_complete_upload_params.UploadCompleteUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Material,
        )

    def create_presigned_url(
        self,
        *,
        content_type: str,
        filename: str,
        name: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UploadCreatePresignedURLResponse:
        """
        Get presigned URL for direct S3 upload

        Args:
          content_type: MIME type of the file

          filename: Filename to upload

          name: Display name for the material

          folder_id: Folder ID to place the material in

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/materials/upload/presigned-url",
            body=maybe_transform(
                {
                    "content_type": content_type,
                    "filename": filename,
                    "name": name,
                    "folder_id": folder_id,
                },
                upload_create_presigned_url_params.UploadCreatePresignedURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UploadCreatePresignedURLResponse,
        )

    def upload_file(
        self,
        *,
        file: FileTypes,
        name: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Material:
        """
        Upload a material file

        Args:
          name: Material name

          folder_id: Folder ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "name": name,
                "folder_id": folder_id,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/api/v1/materials/upload",
            body=maybe_transform(body, upload_upload_file_params.UploadUploadFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Material,
        )

    def upload_file_and_process(
        self,
        *,
        file: FileTypes,
        name: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        poll_interval_ms: float | NotGiven = NOT_GIVEN,
        timeout_ms: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Material:
        """Uploads a file and waits for processing to finish before returning.

        Useful for
        synchronous API usage.

        Args:
          name: Material name

          folder_id: Folder ID (optional)

          poll_interval_ms: Polling interval in milliseconds (default: 2000)

          timeout_ms: Processing timeout in milliseconds (default: 300000)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "name": name,
                "folder_id": folder_id,
                "poll_interval_ms": poll_interval_ms,
                "timeout_ms": timeout_ms,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/api/v1/materials/upload/file-and-process",
            body=maybe_transform(body, upload_upload_file_and_process_params.UploadUploadFileAndProcessParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Material,
        )

    def upload_from_url(
        self,
        *,
        name: str,
        url: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Material:
        """
        Upload material from URL

        Args:
          name: Material name

          url: URL to fetch content from

          folder_id: Folder ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/materials/upload/url",
            body=maybe_transform(
                {
                    "name": name,
                    "url": url,
                    "folder_id": folder_id,
                },
                upload_upload_from_url_params.UploadUploadFromURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Material,
        )

    def upload_url_and_process(
        self,
        *,
        name: str,
        url: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        poll_interval_ms: float | NotGiven = NOT_GIVEN,
        timeout_ms: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Material:
        """
        Fetches content from URL and waits for processing to finish before returning.
        Useful for synchronous API usage.

        Args:
          name: Material name

          url: URL to fetch content from

          folder_id: Folder ID (optional)

          poll_interval_ms: Polling interval in milliseconds (default: 2 seconds)

          timeout_ms: Maximum time to wait for processing in milliseconds (default: 5 minutes)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/materials/upload/url-and-process",
            body=maybe_transform(
                {
                    "name": name,
                    "url": url,
                    "folder_id": folder_id,
                    "poll_interval_ms": poll_interval_ms,
                    "timeout_ms": timeout_ms,
                },
                upload_upload_url_and_process_params.UploadUploadURLAndProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Material,
        )


class AsyncUploadResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUploadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUploadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUploadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GoStudyFetchGo/studyfetch-sdk-python#with_streaming_response
        """
        return AsyncUploadResourceWithStreamingResponse(self)

    async def complete_upload(
        self,
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
    ) -> Material:
        """
        Complete upload after using presigned URL

        Args:
          material_id: The ID of the material that was uploaded

          organization_id: The ID of the organization

          s3_key: The S3 key of the uploaded file

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/materials/upload/complete",
            body=await async_maybe_transform(
                {
                    "material_id": material_id,
                    "organization_id": organization_id,
                    "s3_key": s3_key,
                },
                upload_complete_upload_params.UploadCompleteUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Material,
        )

    async def create_presigned_url(
        self,
        *,
        content_type: str,
        filename: str,
        name: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UploadCreatePresignedURLResponse:
        """
        Get presigned URL for direct S3 upload

        Args:
          content_type: MIME type of the file

          filename: Filename to upload

          name: Display name for the material

          folder_id: Folder ID to place the material in

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/materials/upload/presigned-url",
            body=await async_maybe_transform(
                {
                    "content_type": content_type,
                    "filename": filename,
                    "name": name,
                    "folder_id": folder_id,
                },
                upload_create_presigned_url_params.UploadCreatePresignedURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UploadCreatePresignedURLResponse,
        )

    async def upload_file(
        self,
        *,
        file: FileTypes,
        name: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Material:
        """
        Upload a material file

        Args:
          name: Material name

          folder_id: Folder ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "name": name,
                "folder_id": folder_id,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/api/v1/materials/upload",
            body=await async_maybe_transform(body, upload_upload_file_params.UploadUploadFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Material,
        )

    async def upload_file_and_process(
        self,
        *,
        file: FileTypes,
        name: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        poll_interval_ms: float | NotGiven = NOT_GIVEN,
        timeout_ms: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Material:
        """Uploads a file and waits for processing to finish before returning.

        Useful for
        synchronous API usage.

        Args:
          name: Material name

          folder_id: Folder ID (optional)

          poll_interval_ms: Polling interval in milliseconds (default: 2000)

          timeout_ms: Processing timeout in milliseconds (default: 300000)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "name": name,
                "folder_id": folder_id,
                "poll_interval_ms": poll_interval_ms,
                "timeout_ms": timeout_ms,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/api/v1/materials/upload/file-and-process",
            body=await async_maybe_transform(
                body, upload_upload_file_and_process_params.UploadUploadFileAndProcessParams
            ),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Material,
        )

    async def upload_from_url(
        self,
        *,
        name: str,
        url: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Material:
        """
        Upload material from URL

        Args:
          name: Material name

          url: URL to fetch content from

          folder_id: Folder ID (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/materials/upload/url",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "url": url,
                    "folder_id": folder_id,
                },
                upload_upload_from_url_params.UploadUploadFromURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Material,
        )

    async def upload_url_and_process(
        self,
        *,
        name: str,
        url: str,
        folder_id: str | NotGiven = NOT_GIVEN,
        poll_interval_ms: float | NotGiven = NOT_GIVEN,
        timeout_ms: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Material:
        """
        Fetches content from URL and waits for processing to finish before returning.
        Useful for synchronous API usage.

        Args:
          name: Material name

          url: URL to fetch content from

          folder_id: Folder ID (optional)

          poll_interval_ms: Polling interval in milliseconds (default: 2 seconds)

          timeout_ms: Maximum time to wait for processing in milliseconds (default: 5 minutes)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/materials/upload/url-and-process",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "url": url,
                    "folder_id": folder_id,
                    "poll_interval_ms": poll_interval_ms,
                    "timeout_ms": timeout_ms,
                },
                upload_upload_url_and_process_params.UploadUploadURLAndProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Material,
        )


class UploadResourceWithRawResponse:
    def __init__(self, upload: UploadResource) -> None:
        self._upload = upload

        self.complete_upload = to_raw_response_wrapper(
            upload.complete_upload,
        )
        self.create_presigned_url = to_raw_response_wrapper(
            upload.create_presigned_url,
        )
        self.upload_file = to_raw_response_wrapper(
            upload.upload_file,
        )
        self.upload_file_and_process = to_raw_response_wrapper(
            upload.upload_file_and_process,
        )
        self.upload_from_url = to_raw_response_wrapper(
            upload.upload_from_url,
        )
        self.upload_url_and_process = to_raw_response_wrapper(
            upload.upload_url_and_process,
        )


class AsyncUploadResourceWithRawResponse:
    def __init__(self, upload: AsyncUploadResource) -> None:
        self._upload = upload

        self.complete_upload = async_to_raw_response_wrapper(
            upload.complete_upload,
        )
        self.create_presigned_url = async_to_raw_response_wrapper(
            upload.create_presigned_url,
        )
        self.upload_file = async_to_raw_response_wrapper(
            upload.upload_file,
        )
        self.upload_file_and_process = async_to_raw_response_wrapper(
            upload.upload_file_and_process,
        )
        self.upload_from_url = async_to_raw_response_wrapper(
            upload.upload_from_url,
        )
        self.upload_url_and_process = async_to_raw_response_wrapper(
            upload.upload_url_and_process,
        )


class UploadResourceWithStreamingResponse:
    def __init__(self, upload: UploadResource) -> None:
        self._upload = upload

        self.complete_upload = to_streamed_response_wrapper(
            upload.complete_upload,
        )
        self.create_presigned_url = to_streamed_response_wrapper(
            upload.create_presigned_url,
        )
        self.upload_file = to_streamed_response_wrapper(
            upload.upload_file,
        )
        self.upload_file_and_process = to_streamed_response_wrapper(
            upload.upload_file_and_process,
        )
        self.upload_from_url = to_streamed_response_wrapper(
            upload.upload_from_url,
        )
        self.upload_url_and_process = to_streamed_response_wrapper(
            upload.upload_url_and_process,
        )


class AsyncUploadResourceWithStreamingResponse:
    def __init__(self, upload: AsyncUploadResource) -> None:
        self._upload = upload

        self.complete_upload = async_to_streamed_response_wrapper(
            upload.complete_upload,
        )
        self.create_presigned_url = async_to_streamed_response_wrapper(
            upload.create_presigned_url,
        )
        self.upload_file = async_to_streamed_response_wrapper(
            upload.upload_file,
        )
        self.upload_file_and_process = async_to_streamed_response_wrapper(
            upload.upload_file_and_process,
        )
        self.upload_from_url = async_to_streamed_response_wrapper(
            upload.upload_from_url,
        )
        self.upload_url_and_process = async_to_streamed_response_wrapper(
            upload.upload_url_and_process,
        )
