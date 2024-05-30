import json
from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.vector_store import VectorStore
from openai.types.beta.vector_store_create_params import VectorStoreCreateParams
from openai.types.beta.vector_store_update_params import VectorStoreUpdateParams
from openai.types.beta.vector_store_deleted import VectorStoreDeleted

from ._base import StatefulRoute

from ..helpers.builders.vector_store_files import vector_store_file_from_create_request

from ..stores import StateStore
from .._types.partials.sync_cursor_page import PartialSyncCursorPage
from .._types.partials.vector_stores import (
    PartialVectorStore,
    PartialVectorStoreDeleted,
)

from .._utils.faker import faker
from .._utils.serde import json_loads, model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = [
    "VectorStoreCreateRoute",
    "VectorStoreListRoute",
    "VectorStoreRetrieveRoute",
    "VectorStoreUpdateRoute",
    "VectorStoreDeleteRoute",
]


class VectorStoreCreateRoute(StatefulRoute[VectorStore, PartialVectorStore]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(url__regex="/vector_stores"),
            status_code=201,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route
        model = self._build({}, request)
        self._state.beta.vector_stores.put(model)
        content: VectorStoreCreateParams = json_loads(request.content)
        file_ids = content.get("file_ids", [])
        for file_id in file_ids:
            found_file = self._state.files.get(file_id)
            if not found_file:
                return httpx.Response(404)
            encoded = json.dumps({"file_id": found_file.id})
            create_file_req = httpx.Request(method="", url="", content=encoded)
            vector_store_file = vector_store_file_from_create_request(
                create_file_req,
                extra={"vector_store_id": model.id},
            )
            self._state.beta.vector_stores.files.put(vector_store_file)

        return httpx.Response(status_code=self._status_code, json=model_dict(model))

    @staticmethod
    def _build(partial: PartialVectorStore, request: httpx.Request) -> VectorStore:
        content = json_loads(request.content)
        defaults: PartialVectorStore = {
            "id": faker.beta.vector_store.id(),
            "created_at": utcnow_unix_timestamp_s(),
            "file_counts": {
                "cancelled": 0,
                "completed": len(content.get("file_ids", [])),
                "failed": 0,
                "in_progress": 0,
                "total": 0,
            },
            "name": "",
            "object": "vector_store",
            "status": "completed",
            "usage_bytes": 0,
        }
        if content.get("file_ids"):
            del content["file_ids"]
        return model_parse(VectorStore, defaults | partial | content)


class VectorStoreListRoute(
    StatefulRoute[
        SyncCursorPage[VectorStore], PartialSyncCursorPage[PartialVectorStore]
    ]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(url__regex="/vector_stores"),
            status_code=200,
            state=state,
        )

    @override
    def _handler(self, request: httpx.Request, route: respx.Route) -> httpx.Response:
        self._route = route

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")

        data = self._state.beta.vector_stores.list(limit, order, after, before)
        result_count = len(data)
        total_count = len(self._state.beta.vector_stores.list())
        has_data = bool(result_count)
        has_more = total_count != result_count
        first_id = data[0].id if has_data else None
        last_id = data[-1].id if has_data else None
        model = SyncCursorPage[VectorStore](data=data)
        return httpx.Response(
            status_code=200,
            json=model_dict(model)
            | {"first_id": first_id, "last_id": last_id, "has_more": has_more},
        )

    @staticmethod
    def _build(
        partial: PartialSyncCursorPage[PartialVectorStore],
        request: httpx.Request,
    ) -> SyncCursorPage[VectorStore]:
        raise NotImplementedError


class VectorStoreRetrieveRoute(StatefulRoute[VectorStore, PartialVectorStore]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)"
            ),
            status_code=200,
            state=state,
        )

    @override
    def _handler(
        self,
        request: httpx.Request,
        route: respx.Route,
        **kwargs: Any,
    ) -> httpx.Response:
        self._route = route
        vector_store_id = kwargs["vector_store_id"]
        found = self._state.beta.vector_stores.get(vector_store_id)
        if not found:
            return httpx.Response(404)

        return httpx.Response(status_code=self._status_code, json=model_dict(found))

    @staticmethod
    def _build(partial: PartialVectorStore, request: httpx.Request) -> VectorStore:
        raise NotImplementedError


class VectorStoreUpdateRoute(StatefulRoute[VectorStore, PartialVectorStore]):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)"
            ),
            status_code=200,
            state=state,
        )

    @override
    def _handler(
        self,
        request: httpx.Request,
        route: respx.Route,
        **kwargs: Any,
    ) -> httpx.Response:
        self._route = route
        vector_store_id = kwargs["vector_store_id"]
        found = self._state.beta.vector_stores.get(vector_store_id)
        if not found:
            return httpx.Response(404)

        content: VectorStoreUpdateParams = json_loads(request.content)
        deserialized = model_dict(found)
        updated = model_parse(VectorStore, deserialized | content)
        return httpx.Response(status_code=self._status_code, json=model_dict(updated))

    @staticmethod
    def _build(partial: PartialVectorStore, request: httpx.Request) -> VectorStore:
        raise NotImplementedError


class VectorStoreDeleteRoute(
    StatefulRoute[VectorStoreDeleted, PartialVectorStoreDeleted]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.delete(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)"
            ),
            status_code=200,
            state=state,
        )

    @override
    def _handler(
        self,
        request: httpx.Request,
        route: respx.Route,
        **kwargs: Any,
    ) -> httpx.Response:
        self._route = route
        vector_store_id = kwargs["vector_store_id"]
        deleted = self._state.beta.vector_stores.delete(vector_store_id)
        return httpx.Response(
            status_code=200,
            json=model_dict(
                VectorStoreDeleted(
                    id=vector_store_id,
                    deleted=deleted,
                    object="vector_store.deleted",
                )
            ),
        )

    @staticmethod
    def _build(
        partial: PartialVectorStoreDeleted,
        request: httpx.Request,
    ) -> VectorStoreDeleted:
        raise NotImplementedError
