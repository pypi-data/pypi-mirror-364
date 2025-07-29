# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_complete(self, client: StudyfetchSDK) -> None:
        session = client.v1.scenarios.sessions.complete(
            "sessionId",
        )
        assert session is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_complete(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.sessions.with_raw_response.complete(
            "sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_complete(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.sessions.with_streaming_response.complete(
            "sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_complete(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.v1.scenarios.sessions.with_raw_response.complete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_start(self, client: StudyfetchSDK) -> None:
        session = client.v1.scenarios.sessions.start(
            "id",
        )
        assert session is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_start(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.sessions.with_raw_response.start(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_start(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.sessions.with_streaming_response.start(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_start(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.scenarios.sessions.with_raw_response.start(
                "",
            )


class TestAsyncSessions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_complete(self, async_client: AsyncStudyfetchSDK) -> None:
        session = await async_client.v1.scenarios.sessions.complete(
            "sessionId",
        )
        assert session is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_complete(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.sessions.with_raw_response.complete(
            "sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert session is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_complete(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.sessions.with_streaming_response.complete(
            "sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_complete(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.v1.scenarios.sessions.with_raw_response.complete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_start(self, async_client: AsyncStudyfetchSDK) -> None:
        session = await async_client.v1.scenarios.sessions.start(
            "id",
        )
        assert session is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_start(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.sessions.with_raw_response.start(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert session is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_start(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.sessions.with_streaming_response.start(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_start(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.scenarios.sessions.with_raw_response.start(
                "",
            )
