# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTest:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_cite_image(self, client: StudyfetchSDK) -> None:
        test = client.v1.chat.test.cite_image()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_cite_image(self, client: StudyfetchSDK) -> None:
        response = client.v1.chat.test.with_raw_response.cite_image()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_cite_image(self, client: StudyfetchSDK) -> None:
        with client.v1.chat.test.with_streaming_response.cite_image() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_upload_image(self, client: StudyfetchSDK) -> None:
        test = client.v1.chat.test.upload_image()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_upload_image(self, client: StudyfetchSDK) -> None:
        response = client.v1.chat.test.with_raw_response.upload_image()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_upload_image(self, client: StudyfetchSDK) -> None:
        with client.v1.chat.test.with_streaming_response.upload_image() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True


class TestAsyncTest:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_cite_image(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.chat.test.cite_image()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_cite_image(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.chat.test.with_raw_response.cite_image()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_cite_image(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.chat.test.with_streaming_response.cite_image() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_upload_image(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.chat.test.upload_image()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_upload_image(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.chat.test.with_raw_response.upload_image()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_upload_image(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.chat.test.with_streaming_response.upload_image() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True
