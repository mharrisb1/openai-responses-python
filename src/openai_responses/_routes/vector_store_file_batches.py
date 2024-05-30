import json
from typing import Any
from typing_extensions import override

import httpx
import respx

from openai.pagination import SyncCursorPage
from openai.types.beta.vector_stores.vector_store_file import VectorStoreFile
from openai.types.beta.vector_stores.vector_store_file_batch import VectorStoreFileBatch
from openai.types.beta.vector_stores.file_batch_create_params import (
    FileBatchCreateParams,
)


from ._base import StatefulRoute

from ..helpers.builders.vector_store_files import vector_store_file_from_create_request

from ..stores import StateStore
from .._types.partials.sync_cursor_page import PartialSyncCursorPage
from .._types.partials.vector_store_files import PartialVectorStoreFile
from .._types.partials.vector_store_file_batches import PartialVectorStoreFileBatch

from .._utils.faker import faker
from .._utils.serde import json_loads, model_dict, model_parse
from .._utils.time import utcnow_unix_timestamp_s

__all__ = [
    "VectorStoreFileBatchCreateRoute",
    "VectorStoreFileBatchRetrieveRoute",
    "VectorStoreFileBatchCancelRoute",
    "VectorStoreFileBatchListFilesRoute",
]


class VectorStoreFileBatchCreateRoute(
    StatefulRoute[VectorStoreFileBatch, PartialVectorStoreFileBatch]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)/file_batches"
            ),
            status_code=201,
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
        found_vector_store = self._state.beta.vector_stores.get(vector_store_id)
        if not found_vector_store:
            return httpx.Response(404)

        model = self._build({"vector_store_id": vector_store_id}, request)
        content: FileBatchCreateParams = json_loads(request.content)
        for file_id in content["file_ids"]:
            found_file = self._state.files.get(file_id)
            if not found_file:
                return httpx.Response(404)
            encoded = json.dumps({"file_id": found_file.id})
            create_file_req = httpx.Request(method="", url="", content=encoded)
            vector_store_file = vector_store_file_from_create_request(
                create_file_req,
                extra={"vector_store_id": vector_store_id},
            )
            self._state.beta.vector_stores.files.put(vector_store_file)
            self._state.beta.vector_stores.file_batches.add_related_file(
                model.id,
                vector_store_file.id,
            )

        self._state.beta.vector_stores.file_batches.put(model)
        return httpx.Response(status_code=self._status_code, json=model_dict(model))

    @staticmethod
    def _build(
        partial: PartialVectorStoreFileBatch,
        request: httpx.Request,
    ) -> VectorStoreFileBatch:
        content = json_loads(request.content)
        defaults: PartialVectorStoreFileBatch = {
            "id": faker.beta.vector_store.file_batch.id(),
            "created_at": utcnow_unix_timestamp_s(),
            "file_counts": {
                "cancelled": 0,
                "completed": len(content["file_ids"]),
                "failed": 0,
                "in_progress": 0,
                "total": len(content["file_ids"]),
            },
            "object": "vector_store.files_batch",
            "status": "completed",
        }
        return model_parse(VectorStoreFileBatch, defaults | partial)


class VectorStoreFileBatchRetrieveRoute(
    StatefulRoute[VectorStoreFileBatch, PartialVectorStoreFileBatch]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)/file_batches/(?P<batch_id>[a-zA-Z0-9\_]+)"
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
        found_vector_store = self._state.beta.vector_stores.get(vector_store_id)
        if not found_vector_store:
            return httpx.Response(404)

        batch_id = kwargs["batch_id"]
        found = self._state.beta.vector_stores.file_batches.get(batch_id)
        if not found:
            return httpx.Response(404)

        return httpx.Response(status_code=self._status_code, json=model_dict(found))

    @staticmethod
    def _build(
        partial: PartialVectorStoreFileBatch,
        request: httpx.Request,
    ) -> VectorStoreFileBatch:
        raise NotImplementedError


class VectorStoreFileBatchCancelRoute(
    StatefulRoute[VectorStoreFileBatch, PartialVectorStoreFileBatch]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.post(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)/file_batches/(?P<batch_id>[a-zA-Z0-9\_]+)/cancel"
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
        found_vector_store = self._state.beta.vector_stores.get(vector_store_id)
        if not found_vector_store:
            return httpx.Response(404)

        batch_id = kwargs["batch_id"]
        found = self._state.beta.vector_stores.file_batches.get(batch_id)
        if not found:
            return httpx.Response(404)

        found.status = "cancelled"
        self._state.beta.vector_stores.file_batches.put(found)

        return httpx.Response(status_code=self._status_code, json=model_dict(found))

    @staticmethod
    def _build(
        partial: PartialVectorStoreFileBatch,
        request: httpx.Request,
    ) -> VectorStoreFileBatch:
        raise NotImplementedError


class VectorStoreFileBatchListFilesRoute(
    StatefulRoute[
        SyncCursorPage[VectorStoreFile], PartialSyncCursorPage[PartialVectorStoreFile]
    ]
):
    def __init__(self, router: respx.MockRouter, state: StateStore) -> None:
        super().__init__(
            route=router.get(
                url__regex=r"/vector_stores/(?P<vector_store_id>[a-zA-Z0-9\_]+)/file_batches/(?P<batch_id>[a-zA-Z0-9\_]+)/files"
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
        found_vector_store = self._state.beta.vector_stores.get(vector_store_id)
        if not found_vector_store:
            return httpx.Response(404)

        batch_id = kwargs["batch_id"]
        found = self._state.beta.vector_stores.file_batches.get(batch_id)
        if not found:
            return httpx.Response(404)

        limit = request.url.params.get("limit")
        order = request.url.params.get("order")
        after = request.url.params.get("after")
        before = request.url.params.get("before")
        filter = request.url.params.get("filter")

        data = self._state.beta.vector_stores.list_files_for_batch(
            vector_store_id,
            batch_id,
            limit,
            order,
            after,
            before,
            filter,
        )
        result_count = len(data)
        total_count = len(
            self._state.beta.vector_stores.list_files_for_batch(
                vector_store_id,
                batch_id,
            )
        )
        has_data = bool(result_count)
        has_more = total_count != result_count
        first_id = data[0].id if has_data else None
        last_id = data[-1].id if has_data else None
        model = SyncCursorPage[VectorStoreFile](data=data)
        return httpx.Response(
            status_code=200,
            json=model_dict(model)
            | {"first_id": first_id, "last_id": last_id, "has_more": has_more},
        )

    @staticmethod
    def _build(
        partial: PartialSyncCursorPage[PartialVectorStoreFile],
        request: httpx.Request,
    ) -> SyncCursorPage[VectorStoreFile]:
        raise NotImplementedError
