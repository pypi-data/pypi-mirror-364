# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestScenarios:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: StudyfetchSDK) -> None:
        scenario = client.v1.scenarios.create(
            component_id="componentId",
            name="name",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: StudyfetchSDK) -> None:
        scenario = client.v1.scenarios.create(
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
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.with_raw_response.create(
            component_id="componentId",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.with_streaming_response.create(
            component_id="componentId",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: StudyfetchSDK) -> None:
        scenario = client.v1.scenarios.retrieve(
            "id",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.scenarios.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: StudyfetchSDK) -> None:
        scenario = client.v1.scenarios.update(
            id="id",
            name="name",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: StudyfetchSDK) -> None:
        scenario = client.v1.scenarios.update(
            id="id",
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
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.with_raw_response.update(
            id="id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.with_streaming_response.update(
            id="id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.scenarios.with_raw_response.update(
                id="",
                name="name",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: StudyfetchSDK) -> None:
        scenario = client.v1.scenarios.list()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: StudyfetchSDK) -> None:
        scenario = client.v1.scenarios.delete(
            "id",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.scenarios.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_stats(self, client: StudyfetchSDK) -> None:
        scenario = client.v1.scenarios.get_stats(
            "id",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_stats(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.with_raw_response.get_stats(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_stats(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.with_streaming_response.get_stats(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_stats(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.scenarios.with_raw_response.get_stats(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_submit_answer(self, client: StudyfetchSDK) -> None:
        scenario = client.v1.scenarios.submit_answer(
            id="id",
            conversation_history=[{}],
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_method_submit_answer_with_all_params(self, client: StudyfetchSDK) -> None:
        scenario = client.v1.scenarios.submit_answer(
            id="id",
            conversation_history=[{}],
            final_answer="finalAnswer",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_submit_answer(self, client: StudyfetchSDK) -> None:
        response = client.v1.scenarios.with_raw_response.submit_answer(
            id="id",
            conversation_history=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_submit_answer(self, client: StudyfetchSDK) -> None:
        with client.v1.scenarios.with_streaming_response.submit_answer(
            id="id",
            conversation_history=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_submit_answer(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v1.scenarios.with_raw_response.submit_answer(
                id="",
                conversation_history=[{}],
            )


class TestAsyncScenarios:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncStudyfetchSDK) -> None:
        scenario = await async_client.v1.scenarios.create(
            component_id="componentId",
            name="name",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        scenario = await async_client.v1.scenarios.create(
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
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.with_raw_response.create(
            component_id="componentId",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = await response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.with_streaming_response.create(
            component_id="componentId",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = await response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        scenario = await async_client.v1.scenarios.retrieve(
            "id",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = await response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = await response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.scenarios.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncStudyfetchSDK) -> None:
        scenario = await async_client.v1.scenarios.update(
            id="id",
            name="name",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        scenario = await async_client.v1.scenarios.update(
            id="id",
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
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.with_raw_response.update(
            id="id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = await response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.with_streaming_response.update(
            id="id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = await response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.scenarios.with_raw_response.update(
                id="",
                name="name",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncStudyfetchSDK) -> None:
        scenario = await async_client.v1.scenarios.list()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = await response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = await response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        scenario = await async_client.v1.scenarios.delete(
            "id",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = await response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = await response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.scenarios.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        scenario = await async_client.v1.scenarios.get_stats(
            "id",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.with_raw_response.get_stats(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = await response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.with_streaming_response.get_stats(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = await response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.scenarios.with_raw_response.get_stats(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit_answer(self, async_client: AsyncStudyfetchSDK) -> None:
        scenario = await async_client.v1.scenarios.submit_answer(
            id="id",
            conversation_history=[{}],
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit_answer_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        scenario = await async_client.v1.scenarios.submit_answer(
            id="id",
            conversation_history=[{}],
            final_answer="finalAnswer",
        )
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_submit_answer(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.scenarios.with_raw_response.submit_answer(
            id="id",
            conversation_history=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scenario = await response.parse()
        assert scenario is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_submit_answer(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.scenarios.with_streaming_response.submit_answer(
            id="id",
            conversation_history=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scenario = await response.parse()
            assert scenario is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_submit_answer(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v1.scenarios.with_raw_response.submit_answer(
                id="",
                conversation_history=[{}],
            )
