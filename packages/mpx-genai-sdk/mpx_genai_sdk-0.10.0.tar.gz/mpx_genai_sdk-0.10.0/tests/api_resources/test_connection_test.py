# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from mpx_genai_sdk import Masterpiecex, AsyncMasterpiecex

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConnectionTest:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Masterpiecex) -> None:
        connection_test = client.connection_test.retrieve()
        assert_matches_type(str, connection_test, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Masterpiecex) -> None:
        response = client.connection_test.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection_test = response.parse()
        assert_matches_type(str, connection_test, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Masterpiecex) -> None:
        with client.connection_test.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection_test = response.parse()
            assert_matches_type(str, connection_test, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncConnectionTest:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMasterpiecex) -> None:
        connection_test = await async_client.connection_test.retrieve()
        assert_matches_type(str, connection_test, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMasterpiecex) -> None:
        response = await async_client.connection_test.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        connection_test = await response.parse()
        assert_matches_type(str, connection_test, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMasterpiecex) -> None:
        async with async_client.connection_test.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            connection_test = await response.parse()
            assert_matches_type(str, connection_test, path=["response"])

        assert cast(Any, response.is_closed) is True
