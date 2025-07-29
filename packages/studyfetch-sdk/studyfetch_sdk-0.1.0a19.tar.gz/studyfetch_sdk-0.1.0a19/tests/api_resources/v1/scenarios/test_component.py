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
    def test_method_retrieve(self, client: StudyfetchSDK) -> None:
        component = client.v1.scenarios.component.retrieve(
            "componentId",
        )
        assert component is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.component.with_raw_response.retrieve(
            "componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert component is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.component.with_streaming_response.retrieve(
            "componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.scenarios.component.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: StudyfetchSDK) -> None:
        component = client.v1.scenarios.component.update(
            component_id="componentId",
            name="name",
        )
        assert component is None

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: StudyfetchSDK) -> None:
        component = client.v1.scenarios.component.update(
            component_id="componentId",
            name="name",
            characters=[{}],
            context="context",
            description="description",
            final_answer_prompt="finalAnswerPrompt",
            format="format",
            goal="goal",
            greeting_character_id="greetingCharacterId",
            greeting_message="greetingMessage",
            requires_final_answer=True,
            tools=[{}],
        )
        assert component is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.component.with_raw_response.update(
            component_id="componentId",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert component is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.component.with_streaming_response.update(
            component_id="componentId",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.scenarios.component.with_raw_response.update(
                component_id="",
                name="name",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: StudyfetchSDK) -> None:
        component = client.v1.scenarios.component.delete(
            "componentId",
        )
        assert component is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.component.with_raw_response.delete(
            "componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = response.parse()
        assert component is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.component.with_streaming_response.delete(
            "componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.scenarios.component.with_raw_response.delete(
                "",
            )


class TestAsyncComponent:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.scenarios.component.retrieve(
            "componentId",
        )
        assert component is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.component.with_raw_response.retrieve(
            "componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert component is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.component.with_streaming_response.retrieve(
            "componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.scenarios.component.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.scenarios.component.update(
            component_id="componentId",
            name="name",
        )
        assert component is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.scenarios.component.update(
            component_id="componentId",
            name="name",
            characters=[{}],
            context="context",
            description="description",
            final_answer_prompt="finalAnswerPrompt",
            format="format",
            goal="goal",
            greeting_character_id="greetingCharacterId",
            greeting_message="greetingMessage",
            requires_final_answer=True,
            tools=[{}],
        )
        assert component is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.component.with_raw_response.update(
            component_id="componentId",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert component is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.component.with_streaming_response.update(
            component_id="componentId",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.scenarios.component.with_raw_response.update(
                component_id="",
                name="name",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        component = await async_client.v1.scenarios.component.delete(
            "componentId",
        )
        assert component is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.component.with_raw_response.delete(
            "componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        component = await response.parse()
        assert component is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.component.with_streaming_response.delete(
            "componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            component = await response.parse()
            assert component is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.scenarios.component.with_raw_response.delete(
                "",
            )
