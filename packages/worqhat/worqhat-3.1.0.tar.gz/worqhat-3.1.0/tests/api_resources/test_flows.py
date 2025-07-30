# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from worqhat import Worqhat, AsyncWorqhat
from tests.utils import assert_matches_type
from worqhat.types import FlowRetrieveMetricsResponse
from worqhat._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFlows:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_metrics(self, client: Worqhat) -> None:
        flow = client.flows.retrieve_metrics()
        assert_matches_type(FlowRetrieveMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_metrics_with_all_params(self, client: Worqhat) -> None:
        flow = client.flows.retrieve_metrics(
            end_date=parse_date("2025-07-24"),
            start_date=parse_date("2025-07-01"),
            status="completed",
            user_id="member-test-2f9b9a4f-5898-4e7a-8f26-e60cea49ae31",
        )
        assert_matches_type(FlowRetrieveMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_metrics(self, client: Worqhat) -> None:
        response = client.flows.with_raw_response.retrieve_metrics()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flow = response.parse()
        assert_matches_type(FlowRetrieveMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_metrics(self, client: Worqhat) -> None:
        with client.flows.with_streaming_response.retrieve_metrics() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flow = response.parse()
            assert_matches_type(FlowRetrieveMetricsResponse, flow, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncFlows:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_metrics(self, async_client: AsyncWorqhat) -> None:
        flow = await async_client.flows.retrieve_metrics()
        assert_matches_type(FlowRetrieveMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_metrics_with_all_params(self, async_client: AsyncWorqhat) -> None:
        flow = await async_client.flows.retrieve_metrics(
            end_date=parse_date("2025-07-24"),
            start_date=parse_date("2025-07-01"),
            status="completed",
            user_id="member-test-2f9b9a4f-5898-4e7a-8f26-e60cea49ae31",
        )
        assert_matches_type(FlowRetrieveMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_metrics(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.flows.with_raw_response.retrieve_metrics()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flow = await response.parse()
        assert_matches_type(FlowRetrieveMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_metrics(self, async_client: AsyncWorqhat) -> None:
        async with async_client.flows.with_streaming_response.retrieve_metrics() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flow = await response.parse()
            assert_matches_type(FlowRetrieveMetricsResponse, flow, path=["response"])

        assert cast(Any, response.is_closed) is True
