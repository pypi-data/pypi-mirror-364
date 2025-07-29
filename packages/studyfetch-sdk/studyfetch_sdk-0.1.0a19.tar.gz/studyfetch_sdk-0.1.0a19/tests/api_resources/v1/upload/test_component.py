# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1.upload import (
    FileUploadResponse,
    ComponentCompleteUploadResponse,
    ComponentGetPresignedURLResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestComponent:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_complete_upload(self, client: StudyfetchSDK) -> None:
        component = client.v1.upload.component.complete_upload(
            component_id="componentId",
            material_id="507f1f77bcf86cd799439013",
            organization_id="507f1f77bcf86cd799439011",
            s3_key="organizations/507f1f77bcf86cd799439011/materials/document.pdf",
        )
        assert_matches_type(ComponentCompleteUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_complete_upload(self, client: StudyfetchSDK) -> None:
        response = client.v1.upload.component.with_raw_response.complete_upload(
            component_id="componentId",
            material_id="507f1f77bcf86cd799439013",
            organization_id="507f1f77bcf86cd799439011",
            s3_key="organizations/507f1f77bcf86cd799439011/materials/document.pdf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(ComponentCompleteUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_complete_upload(self, client: StudyfetchSDK) -> None:
        with client.v1.upload.component.with_streaming_response.complete_upload(
            component_id="componentId",
            material_id="507f1f77bcf86cd799439013",
            organization_id="507f1f77bcf86cd799439011",
            s3_key="organizations/507f1f77bcf86cd799439011/materials/document.pdf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(ComponentCompleteUploadResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_complete_upload(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.upload.component.with_raw_response.complete_upload(
                component_id="",
                material_id="507f1f77bcf86cd799439013",
                organization_id="507f1f77bcf86cd799439011",
                s3_key="organizations/507f1f77bcf86cd799439011/materials/document.pdf",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_presigned_url(self, client: StudyfetchSDK) -> None:
        component = client.v1.upload.component.get_presigned_url(
            component_id="componentId",
            content_type="application/pdf",
            filename="document.pdf",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        )
        assert_matches_type(ComponentGetPresignedURLResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_presigned_url(self, client: StudyfetchSDK) -> None:
        response = client.v1.upload.component.with_raw_response.get_presigned_url(
            component_id="componentId",
            content_type="application/pdf",
            filename="document.pdf",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(ComponentGetPresignedURLResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_presigned_url(self, client: StudyfetchSDK) -> None:
        with client.v1.upload.component.with_streaming_response.get_presigned_url(
            component_id="componentId",
            content_type="application/pdf",
            filename="document.pdf",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(ComponentGetPresignedURLResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_presigned_url(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.upload.component.with_raw_response.get_presigned_url(
                component_id="",
                content_type="application/pdf",
                filename="document.pdf",
                folder_id="507f1f77bcf86cd799439012",
                organization_id="507f1f77bcf86cd799439011",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_upload_file(self, client: StudyfetchSDK) -> None:
        component = client.v1.upload.component.upload_file(
            component_id="componentId",
            file=b"raw file contents",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        )
        assert_matches_type(FileUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_upload_file(self, client: StudyfetchSDK) -> None:
        response = client.v1.upload.component.with_raw_response.upload_file(
            component_id="componentId",
            file=b"raw file contents",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(FileUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_upload_file(self, client: StudyfetchSDK) -> None:
        with client.v1.upload.component.with_streaming_response.upload_file(
            component_id="componentId",
            file=b"raw file contents",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(FileUploadResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_upload_file(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.upload.component.with_raw_response.upload_file(
                component_id="",
                file=b"raw file contents",
                folder_id="507f1f77bcf86cd799439012",
                organization_id="507f1f77bcf86cd799439011",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_upload_url(self, client: StudyfetchSDK) -> None:
        component = client.v1.upload.component.upload_url(
            component_id="componentId",
            folder_id="507f1f77bcf86cd799439012",
            name="my-document.pdf",
            organization_id="507f1f77bcf86cd799439011",
            url="https://example.com/document.pdf",
        )
        assert_matches_type(FileUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_upload_url(self, client: StudyfetchSDK) -> None:
        response = client.v1.upload.component.with_raw_response.upload_url(
            component_id="componentId",
            folder_id="507f1f77bcf86cd799439012",
            name="my-document.pdf",
            organization_id="507f1f77bcf86cd799439011",
            url="https://example.com/document.pdf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert_matches_type(FileUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_upload_url(self, client: StudyfetchSDK) -> None:
        with client.v1.upload.component.with_streaming_response.upload_url(
            component_id="componentId",
            folder_id="507f1f77bcf86cd799439012",
            name="my-document.pdf",
            organization_id="507f1f77bcf86cd799439011",
            url="https://example.com/document.pdf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert_matches_type(FileUploadResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_upload_url(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.upload.component.with_raw_response.upload_url(
                component_id="",
                folder_id="507f1f77bcf86cd799439012",
                name="my-document.pdf",
                organization_id="507f1f77bcf86cd799439011",
                url="https://example.com/document.pdf",
            )


class TestAsyncComponent:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_complete_upload(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.upload.component.complete_upload(
            component_id="componentId",
            material_id="507f1f77bcf86cd799439013",
            organization_id="507f1f77bcf86cd799439011",
            s3_key="organizations/507f1f77bcf86cd799439011/materials/document.pdf",
        )
        assert_matches_type(ComponentCompleteUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_complete_upload(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.upload.component.with_raw_response.complete_upload(
            component_id="componentId",
            material_id="507f1f77bcf86cd799439013",
            organization_id="507f1f77bcf86cd799439011",
            s3_key="organizations/507f1f77bcf86cd799439011/materials/document.pdf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(ComponentCompleteUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_complete_upload(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.upload.component.with_streaming_response.complete_upload(
            component_id="componentId",
            material_id="507f1f77bcf86cd799439013",
            organization_id="507f1f77bcf86cd799439011",
            s3_key="organizations/507f1f77bcf86cd799439011/materials/document.pdf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(ComponentCompleteUploadResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_complete_upload(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.upload.component.with_raw_response.complete_upload(
                component_id="",
                material_id="507f1f77bcf86cd799439013",
                organization_id="507f1f77bcf86cd799439011",
                s3_key="organizations/507f1f77bcf86cd799439011/materials/document.pdf",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_presigned_url(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.upload.component.get_presigned_url(
            component_id="componentId",
            content_type="application/pdf",
            filename="document.pdf",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        )
        assert_matches_type(ComponentGetPresignedURLResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_presigned_url(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.upload.component.with_raw_response.get_presigned_url(
            component_id="componentId",
            content_type="application/pdf",
            filename="document.pdf",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(ComponentGetPresignedURLResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_presigned_url(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.upload.component.with_streaming_response.get_presigned_url(
            component_id="componentId",
            content_type="application/pdf",
            filename="document.pdf",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(ComponentGetPresignedURLResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_presigned_url(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.upload.component.with_raw_response.get_presigned_url(
                component_id="",
                content_type="application/pdf",
                filename="document.pdf",
                folder_id="507f1f77bcf86cd799439012",
                organization_id="507f1f77bcf86cd799439011",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_upload_file(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.upload.component.upload_file(
            component_id="componentId",
            file=b"raw file contents",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        )
        assert_matches_type(FileUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_upload_file(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.upload.component.with_raw_response.upload_file(
            component_id="componentId",
            file=b"raw file contents",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(FileUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_upload_file(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.upload.component.with_streaming_response.upload_file(
            component_id="componentId",
            file=b"raw file contents",
            folder_id="507f1f77bcf86cd799439012",
            organization_id="507f1f77bcf86cd799439011",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(FileUploadResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_upload_file(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.upload.component.with_raw_response.upload_file(
                component_id="",
                file=b"raw file contents",
                folder_id="507f1f77bcf86cd799439012",
                organization_id="507f1f77bcf86cd799439011",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_upload_url(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.upload.component.upload_url(
            component_id="componentId",
            folder_id="507f1f77bcf86cd799439012",
            name="my-document.pdf",
            organization_id="507f1f77bcf86cd799439011",
            url="https://example.com/document.pdf",
        )
        assert_matches_type(FileUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_upload_url(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.upload.component.with_raw_response.upload_url(
            component_id="componentId",
            folder_id="507f1f77bcf86cd799439012",
            name="my-document.pdf",
            organization_id="507f1f77bcf86cd799439011",
            url="https://example.com/document.pdf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert_matches_type(FileUploadResponse, component, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_upload_url(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.upload.component.with_streaming_response.upload_url(
            component_id="componentId",
            folder_id="507f1f77bcf86cd799439012",
            name="my-document.pdf",
            organization_id="507f1f77bcf86cd799439011",
            url="https://example.com/document.pdf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert_matches_type(FileUploadResponse, component, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_upload_url(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.upload.component.with_raw_response.upload_url(
                component_id="",
                folder_id="507f1f77bcf86cd799439012",
                name="my-document.pdf",
                organization_id="507f1f77bcf86cd799439011",
                url="https://example.com/document.pdf",
            )
