# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from studyfetch_sdk import StudyfetchSDK, AsyncStudyfetchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTests:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: StudyfetchSDK) -> None:
        test = client.v1.tests.create(
            component_id="componentId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: StudyfetchSDK) -> None:
        test = client.v1.tests.create(
            component_id="componentId",
            name="name",
            user_id="userId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: StudyfetchSDK) -> None:
        response = client.v1.tests.with_raw_response.create(
            component_id="componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: StudyfetchSDK) -> None:
        with client.v1.tests.with_streaming_response.create(
            component_id="componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: StudyfetchSDK) -> None:
        test = client.v1.tests.retrieve(
            "testId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: StudyfetchSDK) -> None:
        response = client.v1.tests.with_raw_response.retrieve(
            "testId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: StudyfetchSDK) -> None:
        with client.v1.tests.with_streaming_response.retrieve(
            "testId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            client.v1.tests.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_results(self, client: StudyfetchSDK) -> None:
        test = client.v1.tests.get_results(
            "testId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_results(self, client: StudyfetchSDK) -> None:
        response = client.v1.tests.with_raw_response.get_results(
            "testId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_results(self, client: StudyfetchSDK) -> None:
        with client.v1.tests.with_streaming_response.get_results(
            "testId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_results(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            client.v1.tests.with_raw_response.get_results(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retake(self, client: StudyfetchSDK) -> None:
        test = client.v1.tests.retake(
            test_id="testId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_method_retake_with_all_params(self, client: StudyfetchSDK) -> None:
        test = client.v1.tests.retake(
            test_id="testId",
            user_id="userId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retake(self, client: StudyfetchSDK) -> None:
        response = client.v1.tests.with_raw_response.retake(
            test_id="testId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retake(self, client: StudyfetchSDK) -> None:
        with client.v1.tests.with_streaming_response.retake(
            test_id="testId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retake(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            client.v1.tests.with_raw_response.retake(
                test_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_submit(self, client: StudyfetchSDK) -> None:
        test = client.v1.tests.submit(
            test_id="testId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_method_submit_with_all_params(self, client: StudyfetchSDK) -> None:
        test = client.v1.tests.submit(
            test_id="testId",
            user_id="userId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_submit(self, client: StudyfetchSDK) -> None:
        response = client.v1.tests.with_raw_response.submit(
            test_id="testId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_submit(self, client: StudyfetchSDK) -> None:
        with client.v1.tests.with_streaming_response.submit(
            test_id="testId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_submit(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            client.v1.tests.with_raw_response.submit(
                test_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_submit_answer(self, client: StudyfetchSDK) -> None:
        test = client.v1.tests.submit_answer(
            test_id="testId",
            answer="answer",
            question_id="questionId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_method_submit_answer_with_all_params(self, client: StudyfetchSDK) -> None:
        test = client.v1.tests.submit_answer(
            test_id="testId",
            answer="answer",
            question_id="questionId",
            user_id="userId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_submit_answer(self, client: StudyfetchSDK) -> None:
        response = client.v1.tests.with_raw_response.submit_answer(
            test_id="testId",
            answer="answer",
            question_id="questionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_submit_answer(self, client: StudyfetchSDK) -> None:
        with client.v1.tests.with_streaming_response.submit_answer(
            test_id="testId",
            answer="answer",
            question_id="questionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_submit_answer(self, client: StudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            client.v1.tests.with_raw_response.submit_answer(
                test_id="",
                answer="answer",
                question_id="questionId",
            )


class TestAsyncTests:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.tests.create(
            component_id="componentId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.tests.create(
            component_id="componentId",
            name="name",
            user_id="userId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.tests.with_raw_response.create(
            component_id="componentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.tests.with_streaming_response.create(
            component_id="componentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.tests.retrieve(
            "testId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.tests.with_raw_response.retrieve(
            "testId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.tests.with_streaming_response.retrieve(
            "testId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            await async_client.v1.tests.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_results(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.tests.get_results(
            "testId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_results(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.tests.with_raw_response.get_results(
            "testId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_results(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.tests.with_streaming_response.get_results(
            "testId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_results(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            await async_client.v1.tests.with_raw_response.get_results(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retake(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.tests.retake(
            test_id="testId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_retake_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.tests.retake(
            test_id="testId",
            user_id="userId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retake(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.tests.with_raw_response.retake(
            test_id="testId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retake(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.tests.with_streaming_response.retake(
            test_id="testId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retake(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            await async_client.v1.tests.with_raw_response.retake(
                test_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.tests.submit(
            test_id="testId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.tests.submit(
            test_id="testId",
            user_id="userId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.tests.with_raw_response.submit(
            test_id="testId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.tests.with_streaming_response.submit(
            test_id="testId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_submit(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            await async_client.v1.tests.with_raw_response.submit(
                test_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit_answer(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.tests.submit_answer(
            test_id="testId",
            answer="answer",
            question_id="questionId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit_answer_with_all_params(self, async_client: AsyncStudyfetchSDK) -> None:
        test = await async_client.v1.tests.submit_answer(
            test_id="testId",
            answer="answer",
            question_id="questionId",
            user_id="userId",
        )
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_submit_answer(self, async_client: AsyncStudyfetchSDK) -> None:
        response = await async_client.v1.tests.with_raw_response.submit_answer(
            test_id="testId",
            answer="answer",
            question_id="questionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert test is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_submit_answer(self, async_client: AsyncStudyfetchSDK) -> None:
        async with async_client.v1.tests.with_streaming_response.submit_answer(
            test_id="testId",
            answer="answer",
            question_id="questionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert test is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_submit_answer(self, async_client: AsyncStudyfetchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `test_id` but received ''"):
            await async_client.v1.tests.with_raw_response.submit_answer(
                test_id="",
                answer="answer",
                question_id="questionId",
            )
