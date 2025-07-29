# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestComponent:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: StudyfetchSDK) -> None:
        component = client.v1.tests.component.list(
            "componentId",
        )
        assert component is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: StudyfetchSDK) -> None:
        response = client.v1.tests.component.with_raw_response.list(
            "componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert component is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: StudyfetchSDK) -> None:
        with client.v1.tests.component.with_streaming_response.list(
            "componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.tests.component.with_raw_response.list(
                "",
            )


class TestAsyncComponent:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.tests.component.list(
            "componentId",
        )
        assert component is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.tests.component.with_raw_response.list(
            "componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert component is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.tests.component.with_streaming_response.list(
            "componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.tests.component.with_raw_response.list(
                "",
            )
