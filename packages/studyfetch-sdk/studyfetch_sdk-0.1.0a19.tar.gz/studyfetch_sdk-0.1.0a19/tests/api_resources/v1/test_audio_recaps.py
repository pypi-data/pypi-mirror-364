# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAudioRecaps:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: StudyfetchSDK) -> None:
        audio_recap = client.v1.audio_recaps.create()
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: StudyfetchSDK) -> None:
        response = client.v1.audio_recaps.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio_recap = response.parse()
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: StudyfetchSDK) -> None:
        with client.v1.audio_recaps.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio_recap = response.parse()
            assert audio_recap is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: StudyfetchSDK) -> None:
        audio_recap = client.v1.audio_recaps.retrieve(
            "recapId",
        )
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: StudyfetchSDK) -> None:
        response = client.v1.audio_recaps.with_raw_response.retrieve(
            "recapId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio_recap = response.parse()
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: StudyfetchSDK) -> None:
        with client.v1.audio_recaps.with_streaming_response.retrieve(
            "recapId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio_recap = response.parse()
            assert audio_recap is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `recap_id` but received ''"):
            client.v1.audio_recaps.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_ask_question(self, client: StudyfetchSDK) -> None:
        audio_recap = client.v1.audio_recaps.ask_question(
            "recapId",
        )
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_ask_question(self, client: StudyfetchSDK) -> None:
        response = client.v1.audio_recaps.with_raw_response.ask_question(
            "recapId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio_recap = response.parse()
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_ask_question(self, client: StudyfetchSDK) -> None:
        with client.v1.audio_recaps.with_streaming_response.ask_question(
            "recapId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio_recap = response.parse()
            assert audio_recap is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_ask_question(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `recap_id` but received ''"):
            client.v1.audio_recaps.with_raw_response.ask_question(
                "",
            )


class TestAsyncAudioRecaps:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncStudyfetchSDK) -> None:
        audio_recap = await async_client.v1.audio_recaps.create()
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.audio_recaps.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio_recap = await response.parse()
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.audio_recaps.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio_recap = await response.parse()
            assert audio_recap is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        audio_recap = await async_client.v1.audio_recaps.retrieve(
            "recapId",
        )
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.audio_recaps.with_raw_response.retrieve(
            "recapId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio_recap = await response.parse()
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.audio_recaps.with_streaming_response.retrieve(
            "recapId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio_recap = await response.parse()
            assert audio_recap is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `recap_id` but received ''"):
            await async_client.v1.audio_recaps.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_ask_question(self, async_client: AsyncStudyfetchSDK) -> None:
        audio_recap = await async_client.v1.audio_recaps.ask_question(
            "recapId",
        )
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_ask_question(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.audio_recaps.with_raw_response.ask_question(
            "recapId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        audio_recap = await response.parse()
        assert audio_recap is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_ask_question(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.audio_recaps.with_streaming_response.ask_question(
            "recapId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            audio_recap = await response.parse()
            assert audio_recap is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_ask_question(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `recap_id` but received ''"):
            await async_client.v1.audio_recaps.with_raw_response.ask_question(
                "",
            )
