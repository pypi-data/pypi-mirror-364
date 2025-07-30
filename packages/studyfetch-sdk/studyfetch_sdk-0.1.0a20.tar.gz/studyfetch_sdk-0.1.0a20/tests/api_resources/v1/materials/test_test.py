# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1.materials import (
    TestPerformOcrResponse,
    TestProcessEpubResponse,
    TestProcessImageResponse,
    TestProcessVideoResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTest:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_perform_ocr(self, client: StudyfetchSDK) -> None:
        test = client.v1.materials.test.perform_ocr()
        assert_matches_type(TestPerformOcrResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_perform_ocr(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.test.with_raw_response.perform_ocr()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestPerformOcrResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_perform_ocr(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.test.with_streaming_response.perform_ocr() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestPerformOcrResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_process_epub(self, client: StudyfetchSDK) -> None:
        test = client.v1.materials.test.process_epub()
        assert_matches_type(TestProcessEpubResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_process_epub(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.test.with_raw_response.process_epub()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestProcessEpubResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_process_epub(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.test.with_streaming_response.process_epub() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestProcessEpubResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_process_image(self, client: StudyfetchSDK) -> None:
        test = client.v1.materials.test.process_image()
        assert_matches_type(TestProcessImageResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_process_image(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.test.with_raw_response.process_image()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestProcessImageResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_process_image(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.test.with_streaming_response.process_image() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestProcessImageResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_process_video(self, client: StudyfetchSDK) -> None:
        test = client.v1.materials.test.process_video()
        assert_matches_type(TestProcessVideoResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_process_video(self, client: StudyfetchSDK) -> None:
        response = client.v1.materials.test.with_raw_response.process_video()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestProcessVideoResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_process_video(self, client: StudyfetchSDK) -> None:
        with client.v1.materials.test.with_streaming_response.process_video() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestProcessVideoResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTest:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_perform_ocr(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.materials.test.perform_ocr()
        assert_matches_type(TestPerformOcrResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_perform_ocr(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.test.with_raw_response.perform_ocr()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestPerformOcrResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_perform_ocr(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.test.with_streaming_response.perform_ocr() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestPerformOcrResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_process_epub(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.materials.test.process_epub()
        assert_matches_type(TestProcessEpubResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_process_epub(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.test.with_raw_response.process_epub()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestProcessEpubResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_process_epub(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.test.with_streaming_response.process_epub() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestProcessEpubResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_process_image(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.materials.test.process_image()
        assert_matches_type(TestProcessImageResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_process_image(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.test.with_raw_response.process_image()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestProcessImageResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_process_image(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.test.with_streaming_response.process_image() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestProcessImageResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_process_video(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.materials.test.process_video()
        assert_matches_type(TestProcessVideoResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_process_video(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.materials.test.with_raw_response.process_video()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestProcessVideoResponse, test, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_process_video(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.materials.test.with_streaming_response.process_video() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestProcessVideoResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True
