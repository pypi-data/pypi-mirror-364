# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDataAnalyst:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_history(self, client: StudyfetchSDK) -> None:
        data_analyst = client.v1.data_analyst.get_history()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_history(self, client: StudyfetchSDK) -> None:
        response = client.v1.data_analyst.with_raw_response.get_history()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_analyst = response.parse()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_history(self, client: StudyfetchSDK) -> None:
        with client.v1.data_analyst.with_streaming_response.get_history() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_analyst = response.parse()
            assert data_analyst is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_session(self, client: StudyfetchSDK) -> None:
        data_analyst = client.v1.data_analyst.retrieve_session(
            session_id="sessionId",
            user_id="userId",
        )
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_session(self, client: StudyfetchSDK) -> None:
        response = client.v1.data_analyst.with_raw_response.retrieve_session(
            session_id="sessionId",
            user_id="userId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_analyst = response.parse()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_session(self, client: StudyfetchSDK) -> None:
        with client.v1.data_analyst.with_streaming_response.retrieve_session(
            session_id="sessionId",
            user_id="userId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_analyst = response.parse()
            assert data_analyst is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_session(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.v1.data_analyst.with_raw_response.retrieve_session(
                session_id="",
                user_id="userId",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_send_followups(self, client: StudyfetchSDK) -> None:
        data_analyst = client.v1.data_analyst.send_followups()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_send_followups(self, client: StudyfetchSDK) -> None:
        response = client.v1.data_analyst.with_raw_response.send_followups()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_analyst = response.parse()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_send_followups(self, client: StudyfetchSDK) -> None:
        with client.v1.data_analyst.with_streaming_response.send_followups() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_analyst = response.parse()
            assert data_analyst is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_send_message(self, client: StudyfetchSDK) -> None:
        data_analyst = client.v1.data_analyst.send_message(
            component_id="componentId",
            message={},
            x_component_id="x-component-id",
        )
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_method_send_message_with_all_params(self, client: StudyfetchSDK) -> None:
        data_analyst = client.v1.data_analyst.send_message(
            component_id="componentId",
            message={
                "images": [
                    {
                        "base64": "base64",
                        "caption": "caption",
                        "mime_type": "mimeType",
                        "url": "url",
                    }
                ],
                "text": "text",
            },
            x_component_id="x-component-id",
            context={},
            group_ids=["class-101", "class-102"],
            session_id="sessionId",
            user_id="userId",
        )
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_send_message(self, client: StudyfetchSDK) -> None:
        response = client.v1.data_analyst.with_raw_response.send_message(
            component_id="componentId",
            message={},
            x_component_id="x-component-id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_analyst = response.parse()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_send_message(self, client: StudyfetchSDK) -> None:
        with client.v1.data_analyst.with_streaming_response.send_message(
            component_id="componentId",
            message={},
            x_component_id="x-component-id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_analyst = response.parse()
            assert data_analyst is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_stream(self, client: StudyfetchSDK) -> None:
        data_analyst = client.v1.data_analyst.stream()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_method_stream_with_all_params(self, client: StudyfetchSDK) -> None:
        data_analyst = client.v1.data_analyst.stream(
            context={},
            group_id="groupId",
            messages=[
                {
                    "content": "content",
                    "role": "user",
                }
            ],
            user_id="userId",
            x_component_id="x-component-id",
        )
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_stream(self, client: StudyfetchSDK) -> None:
        response = client.v1.data_analyst.with_raw_response.stream()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_analyst = response.parse()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_stream(self, client: StudyfetchSDK) -> None:
        with client.v1.data_analyst.with_streaming_response.stream() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_analyst = response.parse()
            assert data_analyst is None

        assert cast(Any, response.is_closed) is True


class TestAsyncDataAnalyst:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_history(self, async_client: AsyncStudyfetchSDK) -> None:
        data_analyst = await async_client.v1.data_analyst.get_history()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_history(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.data_analyst.with_raw_response.get_history()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_analyst = await response.parse()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_history(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.data_analyst.with_streaming_response.get_history() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_analyst = await response.parse()
            assert data_analyst is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_session(self, async_client: AsyncStudyfetchSDK) -> None:
        data_analyst = await async_client.v1.data_analyst.retrieve_session(
            session_id="sessionId",
            user_id="userId",
        )
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_session(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.data_analyst.with_raw_response.retrieve_session(
            session_id="sessionId",
            user_id="userId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_analyst = await response.parse()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_session(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.data_analyst.with_streaming_response.retrieve_session(
            session_id="sessionId",
            user_id="userId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_analyst = await response.parse()
            assert data_analyst is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_session(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.v1.data_analyst.with_raw_response.retrieve_session(
                session_id="",
                user_id="userId",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_send_followups(self, async_client: AsyncStudyfetchSDK) -> None:
        data_analyst = await async_client.v1.data_analyst.send_followups()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_send_followups(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.data_analyst.with_raw_response.send_followups()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_analyst = await response.parse()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_send_followups(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.data_analyst.with_streaming_response.send_followups() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_analyst = await response.parse()
            assert data_analyst is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_send_message(self, async_client: AsyncStudyfetchSDK) -> None:
        data_analyst = await async_client.v1.data_analyst.send_message(
            component_id="componentId",
            message={},
            x_component_id="x-component-id",
        )
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_send_message_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        data_analyst = await async_client.v1.data_analyst.send_message(
            component_id="componentId",
            message={
                "images": [
                    {
                        "base64": "base64",
                        "caption": "caption",
                        "mime_type": "mimeType",
                        "url": "url",
                    }
                ],
                "text": "text",
            },
            x_component_id="x-component-id",
            context={},
            group_ids=["class-101", "class-102"],
            session_id="sessionId",
            user_id="userId",
        )
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_send_message(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.data_analyst.with_raw_response.send_message(
            component_id="componentId",
            message={},
            x_component_id="x-component-id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_analyst = await response.parse()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_send_message(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.data_analyst.with_streaming_response.send_message(
            component_id="componentId",
            message={},
            x_component_id="x-component-id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_analyst = await response.parse()
            assert data_analyst is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_stream(self, async_client: AsyncStudyfetchSDK) -> None:
        data_analyst = await async_client.v1.data_analyst.stream()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_stream_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        data_analyst = await async_client.v1.data_analyst.stream(
            context={},
            group_id="groupId",
            messages=[
                {
                    "content": "content",
                    "role": "user",
                }
            ],
            user_id="userId",
            x_component_id="x-component-id",
        )
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_stream(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.data_analyst.with_raw_response.stream()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_analyst = await response.parse()
        assert data_analyst is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_stream(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.data_analyst.with_streaming_response.stream() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_analyst = await response.parse()
            assert data_analyst is None

        assert cast(Any, response.is_closed) is True
