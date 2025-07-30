# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import date
from typing_extensions import Literal

import httpx

from ..types import flow_retrieve_metrics_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.flow_retrieve_metrics_response import FlowRetrieveMetricsResponse

__all__ = ["FlowsResource", "AsyncFlowsResource"]


class FlowsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FlowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return FlowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FlowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return FlowsResourceWithStreamingResponse(self)

    def retrieve_metrics(
        self,
        *,
        end_date: Union[str, date] | NotGiven = NOT_GIVEN,
        start_date: Union[str, date] | NotGiven = NOT_GIVEN,
        status: Literal["completed", "failed", "in_progress"] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlowRetrieveMetricsResponse:
        """Get metrics for workflows within a specified date range.

        This endpoint provides
        aggregated statistics about workflow execution and detailed information about
        individual workflows.

        The response includes metrics aggregated by user and a list of all workflows
        matching the specified criteria.

        Args:
          end_date: End date for filtering (YYYY-MM-DD format)

          start_date: Start date for filtering (YYYY-MM-DD format)

          status: Filter by workflow status

          user_id: Filter by specific user ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/flows/metrics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "start_date": start_date,
                        "status": status,
                        "user_id": user_id,
                    },
                    flow_retrieve_metrics_params.FlowRetrieveMetricsParams,
                ),
            ),
            cast_to=FlowRetrieveMetricsResponse,
        )


class AsyncFlowsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFlowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncFlowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFlowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return AsyncFlowsResourceWithStreamingResponse(self)

    async def retrieve_metrics(
        self,
        *,
        end_date: Union[str, date] | NotGiven = NOT_GIVEN,
        start_date: Union[str, date] | NotGiven = NOT_GIVEN,
        status: Literal["completed", "failed", "in_progress"] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlowRetrieveMetricsResponse:
        """Get metrics for workflows within a specified date range.

        This endpoint provides
        aggregated statistics about workflow execution and detailed information about
        individual workflows.

        The response includes metrics aggregated by user and a list of all workflows
        matching the specified criteria.

        Args:
          end_date: End date for filtering (YYYY-MM-DD format)

          start_date: Start date for filtering (YYYY-MM-DD format)

          status: Filter by workflow status

          user_id: Filter by specific user ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/flows/metrics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "start_date": start_date,
                        "status": status,
                        "user_id": user_id,
                    },
                    flow_retrieve_metrics_params.FlowRetrieveMetricsParams,
                ),
            ),
            cast_to=FlowRetrieveMetricsResponse,
        )


class FlowsResourceWithRawResponse:
    def __init__(self, flows: FlowsResource) -> None:
        self._flows = flows

        self.retrieve_metrics = to_raw_response_wrapper(
            flows.retrieve_metrics,
        )


class AsyncFlowsResourceWithRawResponse:
    def __init__(self, flows: AsyncFlowsResource) -> None:
        self._flows = flows

        self.retrieve_metrics = async_to_raw_response_wrapper(
            flows.retrieve_metrics,
        )


class FlowsResourceWithStreamingResponse:
    def __init__(self, flows: FlowsResource) -> None:
        self._flows = flows

        self.retrieve_metrics = to_streamed_response_wrapper(
            flows.retrieve_metrics,
        )


class AsyncFlowsResourceWithStreamingResponse:
    def __init__(self, flows: AsyncFlowsResource) -> None:
        self._flows = flows

        self.retrieve_metrics = async_to_streamed_response_wrapper(
            flows.retrieve_metrics,
        )
