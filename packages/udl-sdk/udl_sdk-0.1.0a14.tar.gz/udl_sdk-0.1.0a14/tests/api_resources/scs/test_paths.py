# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from unifieddatalibrary import Unifieddatalibrary, AsyncUnifieddatalibrary

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPaths:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Unifieddatalibrary) -> None:
        path = client.scs.paths.create(
            id="id",
            classification_marking="classificationMarking",
            body=b"raw file contents",
        )
        assert_matches_type(str, path, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Unifieddatalibrary) -> None:
        path = client.scs.paths.create(
            id="id",
            classification_marking="classificationMarking",
            body=b"raw file contents",
            delete_after="deleteAfter",
            description="description",
            overwrite=True,
            send_notification=True,
            tags="tags",
        )
        assert_matches_type(str, path, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Unifieddatalibrary) -> None:
        response = client.scs.paths.with_raw_response.create(
            id="id",
            classification_marking="classificationMarking",
            body=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        path = response.parse()
        assert_matches_type(str, path, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Unifieddatalibrary) -> None:
        with client.scs.paths.with_streaming_response.create(
            id="id",
            classification_marking="classificationMarking",
            body=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            path = response.parse()
            assert_matches_type(str, path, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPaths:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncUnifieddatalibrary) -> None:
        path = await async_client.scs.paths.create(
            id="id",
            classification_marking="classificationMarking",
            body=b"raw file contents",
        )
        assert_matches_type(str, path, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncUnifieddatalibrary) -> None:
        path = await async_client.scs.paths.create(
            id="id",
            classification_marking="classificationMarking",
            body=b"raw file contents",
            delete_after="deleteAfter",
            description="description",
            overwrite=True,
            send_notification=True,
            tags="tags",
        )
        assert_matches_type(str, path, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncUnifieddatalibrary) -> None:
        response = await async_client.scs.paths.with_raw_response.create(
            id="id",
            classification_marking="classificationMarking",
            body=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        path = await response.parse()
        assert_matches_type(str, path, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncUnifieddatalibrary) -> None:
        async with async_client.scs.paths.with_streaming_response.create(
            id="id",
            classification_marking="classificationMarking",
            body=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            path = await response.parse()
            assert_matches_type(str, path, path=["response"])

        assert cast(Any, response.is_closed) is True
