# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExplainers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: StudyfetchSDK) -> None:
        explainer = client.v1.explainers.create(
            component_id="componentId",
            folder_ids=["string"],
            material_ids=["string"],
            target_length=15,
            title="title",
        )
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: StudyfetchSDK) -> None:
        explainer = client.v1.explainers.create(
            component_id="componentId",
            folder_ids=["string"],
            material_ids=["string"],
            target_length=15,
            title="title",
            image_search=True,
            model="gpt-4o-mini-2024-07-18",
            style="professional",
            user_id="userId",
            vertical_video=True,
            web_search=True,
        )
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: StudyfetchSDK) -> None:
        response = client.v1.explainers.with_raw_response.create(
            component_id="componentId",
            folder_ids=["string"],
            material_ids=["string"],
            target_length=15,
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        explainer = response.parse()
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: StudyfetchSDK) -> None:
        with client.v1.explainers.with_streaming_response.create(
            component_id="componentId",
            folder_ids=["string"],
            material_ids=["string"],
            target_length=15,
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            explainer = response.parse()
            assert explainer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: StudyfetchSDK) -> None:
        explainer = client.v1.explainers.retrieve(
            "componentId",
        )
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: StudyfetchSDK) -> None:
        response = client.v1.explainers.with_raw_response.retrieve(
            "componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        explainer = response.parse()
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: StudyfetchSDK) -> None:
        with client.v1.explainers.with_streaming_response.retrieve(
            "componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            explainer = response.parse()
            assert explainer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.explainers.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_handle_webhook(self, client: StudyfetchSDK) -> None:
        explainer = client.v1.explainers.handle_webhook(
            event="video.completed",
            video={"id": "id"},
        )
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    def test_method_handle_webhook_with_all_params(self, client: StudyfetchSDK) -> None:
        explainer = client.v1.explainers.handle_webhook(
            event="video.completed",
            video={
                "id": "id",
                "image_sources": {},
                "progress": 0,
                "sections": ["string"],
                "stream_id": "streamId",
                "stream_url": "streamUrl",
                "thumbnail_url": "thumbnailUrl",
                "transcript": "transcript",
                "video_url": "videoUrl",
                "web_search_results": {},
                "web_search_sources": {},
            },
        )
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_handle_webhook(self, client: StudyfetchSDK) -> None:
        response = client.v1.explainers.with_raw_response.handle_webhook(
            event="video.completed",
            video={"id": "id"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        explainer = response.parse()
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_handle_webhook(self, client: StudyfetchSDK) -> None:
        with client.v1.explainers.with_streaming_response.handle_webhook(
            event="video.completed",
            video={"id": "id"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            explainer = response.parse()
            assert explainer is None

        assert cast(Any, response.is_closed) is True


class TestAsyncExplainers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncStudyfetchSDK) -> None:
        explainer = await async_client.v1.explainers.create(
            component_id="componentId",
            folder_ids=["string"],
            material_ids=["string"],
            target_length=15,
            title="title",
        )
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        explainer = await async_client.v1.explainers.create(
            component_id="componentId",
            folder_ids=["string"],
            material_ids=["string"],
            target_length=15,
            title="title",
            image_search=True,
            model="gpt-4o-mini-2024-07-18",
            style="professional",
            user_id="userId",
            vertical_video=True,
            web_search=True,
        )
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.explainers.with_raw_response.create(
            component_id="componentId",
            folder_ids=["string"],
            material_ids=["string"],
            target_length=15,
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        explainer = await response.parse()
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.explainers.with_streaming_response.create(
            component_id="componentId",
            folder_ids=["string"],
            material_ids=["string"],
            target_length=15,
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            explainer = await response.parse()
            assert explainer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        explainer = await async_client.v1.explainers.retrieve(
            "componentId",
        )
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.explainers.with_raw_response.retrieve(
            "componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        explainer = await response.parse()
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.explainers.with_streaming_response.retrieve(
            "componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            explainer = await response.parse()
            assert explainer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.explainers.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_handle_webhook(self, async_client: AsyncStudyfetchSDK) -> None:
        explainer = await async_client.v1.explainers.handle_webhook(
            event="video.completed",
            video={"id": "id"},
        )
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_handle_webhook_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        explainer = await async_client.v1.explainers.handle_webhook(
            event="video.completed",
            video={
                "id": "id",
                "image_sources": {},
                "progress": 0,
                "sections": ["string"],
                "stream_id": "streamId",
                "stream_url": "streamUrl",
                "thumbnail_url": "thumbnailUrl",
                "transcript": "transcript",
                "video_url": "videoUrl",
                "web_search_results": {},
                "web_search_sources": {},
            },
        )
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_handle_webhook(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.explainers.with_raw_response.handle_webhook(
            event="video.completed",
            video={"id": "id"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        explainer = await response.parse()
        assert explainer is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_handle_webhook(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.explainers.with_streaming_response.handle_webhook(
            event="video.completed",
            video={"id": "id"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            explainer = await response.parse()
            assert explainer is None

        assert cast(Any, response.is_closed) is True
