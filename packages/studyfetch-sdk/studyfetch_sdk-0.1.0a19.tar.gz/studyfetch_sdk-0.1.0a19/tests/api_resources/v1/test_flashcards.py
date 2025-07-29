# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK
from studyfetch_sdk.types.v1 import (
    FlashcardGetTypesResponse,
    FlashcardBatchProcessResponse,
    FlashcardGetAlgorithmResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFlashcards:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_batch_process(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.batch_process(
            component_id="componentId",
            operations=[
                {
                    "action": "rate",
                    "card_id": "cardId",
                }
            ],
        )
        assert_matches_type(FlashcardBatchProcessResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_batch_process_with_all_params(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.batch_process(
            component_id="componentId",
            operations=[
                {
                    "action": "rate",
                    "card_id": "cardId",
                    "group_id": "groupId",
                    "rating": 0,
                    "user_id": "userId",
                }
            ],
            group_id="groupId",
            user_id="userId",
        )
        assert_matches_type(FlashcardBatchProcessResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_batch_process(self, client: StudyfetchSDK) -> None:
        response = client.v1.flashcards.with_raw_response.batch_process(
            component_id="componentId",
            operations=[
                {
                    "action": "rate",
                    "card_id": "cardId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = response.parse()
        assert_matches_type(FlashcardBatchProcessResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_batch_process(self, client: StudyfetchSDK) -> None:
        with client.v1.flashcards.with_streaming_response.batch_process(
            component_id="componentId",
            operations=[
                {
                    "action": "rate",
                    "card_id": "cardId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = response.parse()
            assert_matches_type(FlashcardBatchProcessResponse, flashcard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_batch_process(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.flashcards.with_raw_response.batch_process(
                component_id="",
                operations=[
                    {
                        "action": "rate",
                        "card_id": "cardId",
                    }
                ],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_algorithm(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.get_algorithm()
        assert_matches_type(FlashcardGetAlgorithmResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_algorithm(self, client: StudyfetchSDK) -> None:
        response = client.v1.flashcards.with_raw_response.get_algorithm()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = response.parse()
        assert_matches_type(FlashcardGetAlgorithmResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_algorithm(self, client: StudyfetchSDK) -> None:
        with client.v1.flashcards.with_streaming_response.get_algorithm() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = response.parse()
            assert_matches_type(FlashcardGetAlgorithmResponse, flashcard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_all(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.get_all(
            component_id="componentId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_method_get_all_with_all_params(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.get_all(
            component_id="componentId",
            group_ids="groupIds",
            limit=0,
            offset=0,
            user_id="userId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_all(self, client: StudyfetchSDK) -> None:
        response = client.v1.flashcards.with_raw_response.get_all(
            component_id="componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = response.parse()
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_all(self, client: StudyfetchSDK) -> None:
        with client.v1.flashcards.with_streaming_response.get_all(
            component_id="componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = response.parse()
            assert flashcard is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_all(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.flashcards.with_raw_response.get_all(
                component_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_due(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.get_due(
            component_id="componentId",
            group_ids="groupIds",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_method_get_due_with_all_params(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.get_due(
            component_id="componentId",
            group_ids="groupIds",
            limit=0,
            user_id="userId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_due(self, client: StudyfetchSDK) -> None:
        response = client.v1.flashcards.with_raw_response.get_due(
            component_id="componentId",
            group_ids="groupIds",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = response.parse()
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_due(self, client: StudyfetchSDK) -> None:
        with client.v1.flashcards.with_streaming_response.get_due(
            component_id="componentId",
            group_ids="groupIds",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = response.parse()
            assert flashcard is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_due(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.flashcards.with_raw_response.get_due(
                component_id="",
                group_ids="groupIds",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_stats(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.get_stats(
            component_id="componentId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_method_get_stats_with_all_params(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.get_stats(
            component_id="componentId",
            group_ids="groupIds",
            user_id="userId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_stats(self, client: StudyfetchSDK) -> None:
        response = client.v1.flashcards.with_raw_response.get_stats(
            component_id="componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = response.parse()
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_stats(self, client: StudyfetchSDK) -> None:
        with client.v1.flashcards.with_streaming_response.get_stats(
            component_id="componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = response.parse()
            assert flashcard is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_stats(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.flashcards.with_raw_response.get_stats(
                component_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_types(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.get_types()
        assert_matches_type(FlashcardGetTypesResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_types(self, client: StudyfetchSDK) -> None:
        response = client.v1.flashcards.with_raw_response.get_types()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = response.parse()
        assert_matches_type(FlashcardGetTypesResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_types(self, client: StudyfetchSDK) -> None:
        with client.v1.flashcards.with_streaming_response.get_types() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = response.parse()
            assert_matches_type(FlashcardGetTypesResponse, flashcard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_rate(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.rate(
            component_id="componentId",
            card_id="cardId",
            rating=0,
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_method_rate_with_all_params(self, client: StudyfetchSDK) -> None:
        flashcard = client.v1.flashcards.rate(
            component_id="componentId",
            card_id="cardId",
            rating=0,
            group_id="groupId",
            user_id="userId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_rate(self, client: StudyfetchSDK) -> None:
        response = client.v1.flashcards.with_raw_response.rate(
            component_id="componentId",
            card_id="cardId",
            rating=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = response.parse()
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_rate(self, client: StudyfetchSDK) -> None:
        with client.v1.flashcards.with_streaming_response.rate(
            component_id="componentId",
            card_id="cardId",
            rating=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = response.parse()
            assert flashcard is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_rate(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            client.v1.flashcards.with_raw_response.rate(
                component_id="",
                card_id="cardId",
                rating=0,
            )


class TestAsyncFlashcards:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_batch_process(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.batch_process(
            component_id="componentId",
            operations=[
                {
                    "action": "rate",
                    "card_id": "cardId",
                }
            ],
        )
        assert_matches_type(FlashcardBatchProcessResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_batch_process_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.batch_process(
            component_id="componentId",
            operations=[
                {
                    "action": "rate",
                    "card_id": "cardId",
                    "group_id": "groupId",
                    "rating": 0,
                    "user_id": "userId",
                }
            ],
            group_id="groupId",
            user_id="userId",
        )
        assert_matches_type(FlashcardBatchProcessResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_batch_process(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.flashcards.with_raw_response.batch_process(
            component_id="componentId",
            operations=[
                {
                    "action": "rate",
                    "card_id": "cardId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = await response.parse()
        assert_matches_type(FlashcardBatchProcessResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_batch_process(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.flashcards.with_streaming_response.batch_process(
            component_id="componentId",
            operations=[
                {
                    "action": "rate",
                    "card_id": "cardId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = await response.parse()
            assert_matches_type(FlashcardBatchProcessResponse, flashcard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_batch_process(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.flashcards.with_raw_response.batch_process(
                component_id="",
                operations=[
                    {
                        "action": "rate",
                        "card_id": "cardId",
                    }
                ],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_algorithm(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.get_algorithm()
        assert_matches_type(FlashcardGetAlgorithmResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_algorithm(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.flashcards.with_raw_response.get_algorithm()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = await response.parse()
        assert_matches_type(FlashcardGetAlgorithmResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_algorithm(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.flashcards.with_streaming_response.get_algorithm() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = await response.parse()
            assert_matches_type(FlashcardGetAlgorithmResponse, flashcard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_all(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.get_all(
            component_id="componentId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_all_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.get_all(
            component_id="componentId",
            group_ids="groupIds",
            limit=0,
            offset=0,
            user_id="userId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_all(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.flashcards.with_raw_response.get_all(
            component_id="componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = await response.parse()
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_all(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.flashcards.with_streaming_response.get_all(
            component_id="componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = await response.parse()
            assert flashcard is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_all(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.flashcards.with_raw_response.get_all(
                component_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_due(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.get_due(
            component_id="componentId",
            group_ids="groupIds",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_due_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.get_due(
            component_id="componentId",
            group_ids="groupIds",
            limit=0,
            user_id="userId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_due(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.flashcards.with_raw_response.get_due(
            component_id="componentId",
            group_ids="groupIds",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = await response.parse()
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_due(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.flashcards.with_streaming_response.get_due(
            component_id="componentId",
            group_ids="groupIds",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = await response.parse()
            assert flashcard is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_due(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.flashcards.with_raw_response.get_due(
                component_id="",
                group_ids="groupIds",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.get_stats(
            component_id="componentId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_stats_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.get_stats(
            component_id="componentId",
            group_ids="groupIds",
            user_id="userId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.flashcards.with_raw_response.get_stats(
            component_id="componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = await response.parse()
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.flashcards.with_streaming_response.get_stats(
            component_id="componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = await response.parse()
            assert flashcard is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_stats(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.flashcards.with_raw_response.get_stats(
                component_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_types(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.get_types()
        assert_matches_type(FlashcardGetTypesResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_types(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.flashcards.with_raw_response.get_types()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = await response.parse()
        assert_matches_type(FlashcardGetTypesResponse, flashcard, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_types(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.flashcards.with_streaming_response.get_types() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = await response.parse()
            assert_matches_type(FlashcardGetTypesResponse, flashcard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_rate(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.rate(
            component_id="componentId",
            card_id="cardId",
            rating=0,
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_rate_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        flashcard = await async_client.v1.flashcards.rate(
            component_id="componentId",
            card_id="cardId",
            rating=0,
            group_id="groupId",
            user_id="userId",
        )
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_rate(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.flashcards.with_raw_response.rate(
            component_id="componentId",
            card_id="cardId",
            rating=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flashcard = await response.parse()
        assert flashcard is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_rate(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.flashcards.with_streaming_response.rate(
            component_id="componentId",
            card_id="cardId",
            rating=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flashcard = await response.parse()
            assert flashcard is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_rate(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `component_id` but received ''"):
            await async_client.v1.flashcards.with_raw_response.rate(
                component_id="",
                card_id="cardId",
                rating=0,
            )
